import time
import socket
import random
import struct
import select
import logging
import ipaddress

from .utils import Utils

SMEEX_UDP_WELL_KNOWN_PORT = 17737


def _get_network_interfaces_using_ifaddr(one_ip_per_adapter=False):
    logging.info("List interfaces with ifaddr...")
    netif_ip_list = []
    try:
        import ifaddr
    except Exception as ex:
        print("Error, module 'ifaddr' not installed.")
        logging.error("Error, module 'ifaddr' not installed.")
        return None

    adapters = ifaddr.get_adapters()
    logging.info("Found %d interfaces" % len(adapters))
    for adapter in adapters:
        ipv4_address_found = False
        print("IPs of network adapter ", adapter.nice_name)
        for ip in adapter.ips:
            if ip.ip.count('.') != 3:
                continue
            ipv4_address_found = True
            logging.info("--> " + str(ip.ip) + "/" + str(ip.network_prefix))
            result = (adapter, ip.ip)
            netif_ip_list.append(result)
            if one_ip_per_adapter:
                break

        if not ipv4_address_found:
            logging.info("No IPv4 addresses found.")

    return netif_ip_list


def _discover_modules_on_netif(netif_ip_tuple, num_attempts=1, per_attempt_timeout=0.5, ma_sleep_min=0.2, ma_sleep_max=0.5):
    """ Discover modules on the network interface with the specified IP address."""
    modules_found = {}

    # Apply a sensible minimum to the timeout
    if per_attempt_timeout < 0.1:
        per_attempt_timeout = 0.1

    # Apply limits to the num_attempts
    if num_attempts < 0:
        num_attempts = 1
    if num_attempts > 6:
        num_attempts = 6

    # Allow the OS to issue us a local port number, then reuse the number for the second socket
    local_listen_port = 0
    # I could not get consistently good results with properly calculated size, so just use a big number.
    # Plan for around 300 bytes MINIMUM per module, especially on a CPU constrained system.
    recv_buf_size = (1000 * 500)  # 500k/0.1s-OK, 100k/0.1s-OK
    # Just a safety limit to prevent run-away memory allocation. We should never see 1000 responses, let alone more
    # Do not set this too low though because on Windows, if all modules respond with broadcasts, our internal list
    # will hold all responses twice.
    max_responses = 5000
    # The size of the biggest response we expect
    max_payload_len = 1500

    try:
        # First socket. Used for sending the discover packets and receiving some/all responses
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_sock.setblocking(False)
        # I'm still not sure why, but if we don't set socket.SO_REUSEADDR on this first socket,
        # under Linux, the second socket's bind fails.
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # Since we will be sending broadcast packets, we need to enable this for the socket
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        # Update the receive buffer space as we expect a burst of small packets
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buf_size)
        # Bind to the address given to us. This should be the normal unicast IP address associated with
        # this network interface. Under Windows, this is enough and we are able to send a broadcast and consequently
        # receive all unicast and broadcast responses. Under Linux, we get the same except for the broadcast responses.
        send_sock.bind((netif_ip_tuple[1], local_listen_port))
        # Now that Bind has succeeded, retrieve the port number that was assigned to us and store it for later use.
        # We will need this under Linux to open a second socket that only receives broadcast responses.
        local_listen_port = send_sock.getsockname()[1]

        # On Linux, we cannot send a broadcast and also receive all unicast/broadcast responses.
        # Because of that, we will open a second socket for receiving broadcasts.
        bcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bcast_sock.setblocking(False)
        # Since we're binding to a wildcard address, our first socket will interfere with this socket's bind
        # therefore, we have to set socket.SO_REUSEADDR.
        bcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # Note: this socket will never send anything, so we don't need socket.SO_BROADCAST
        # bcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        # Update the receive buffer space as we expect a burst of small packets
        bcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buf_size)
        # Bind to the wildcard address and the same port number as the first socket.
        # Under Linux, this allows us to collect responses sent to 255.255.255.255 which we would not get
        # through the original socket.
        bcast_sock.bind(('', local_listen_port))
    except Exception as exc:
        logging.error(type(exc).__name__)
        # Logger.log(logging.DEBUG, exc.__class__.__name__)
        return

    # Ready to do module discovery.
    # Do it as many times as were requested
    for iteration in range(num_attempts):
        # If we're doing multiple attempts, add a small random delay to consecutive
        # attempts, so that we don't abuse the network too much
        if iteration != 0:
            sleep_time = random.uniform(ma_sleep_min, ma_sleep_max)
            # Logger.log(logging.DEBUG, str(iteration) + ": Goint to sleep for " + str(sleep_time) + " seconds")
            time.sleep(sleep_time)
        # logging.info("Attempt: " + str(iteration))

        response_list = []  # Always start with a brand new clean list

        # Generate a session ID that ties requests and responses together
        my_session_id = random.randint(1, 0xFFFFFFFF)
        # Construct the Discover All packet
        svc_name = "Identity"
        svc_name_len = min(16, len(svc_name))
        padding = 16 - svc_name_len
        payload = struct.pack(">BII", 0x05, my_session_id, 0) + bytes("Identity", 'ascii') + bytearray(padding)
        # Send it to 255.255.255.255
        send_sock.sendto(payload, ('<broadcast>', SMEEX_UDP_WELL_KNOWN_PORT))

        internal_list_full = False
        while not internal_list_full:
            # this will block until at least one socket is ready
            ready_socks, _, _ = select.select([send_sock, bcast_sock], [], [], per_attempt_timeout)
            if len(ready_socks) == 0:
                # select timed out, so nothing was received for a long enough time. We are done here
                break
            # Go through the list of ready sockets and consume all the buffered packets
            for ready_socket in ready_socks:
                # Try to consume as many packets in one go as possible. Calling recv() multiple times
                # appears to be more efficient that multiple select calls and works more reliably with smaller
                # socket buffer sizes. Don't go overboard though, there's another socket that may be buffering data.
                packets_per_select = 0
                while True:
                    try:
                        discover_response = ready_socket.recv(max_payload_len)
                    except:
                        # We probably for EWOULDBLOCK or something similar. Just keep on trucking
                        break
                    else:
                        # Store this response of later
                        response_list.append(discover_response)
                        if len(response_list) >= max_responses:
                            logging.error("Too many responses.... quitting.")
                            internal_list_full = True
                            break
                        packets_per_select += 1
                        if packets_per_select > 20:
                            break  # Give the other socket a chance
        # while not internal_list_full:

        # print(f"Parsing {len(response_list)} responses...")
        # Parse all responses and populate the list of unique modules
        for resp in response_list:
            # If we end up receiving our own request or other packets that don't fit the unpack string,
            # we get and exception, so keep the unpacking in a try block
            try:
                (op_code, their_session_recv, my_session_recv) = struct.unpack(">BII", resp[0:9])
                if my_session_id != my_session_recv:
                    continue

                # Remove 9 bytes header
                data = resp[9:]

                module_object = Utils.decode_discover_data(data)
                sn = None

                if module_object is not None:
                    module_object['netif'] = netif_ip_tuple[0]
                    sn = module_object['sn']

            except struct.error:
                continue

            if op_code != 0x80:
                continue

            if sn not in modules_found:
                modules_found[sn] = module_object
        # for resp in response_list:
    # for iteration in range(num_attempts):

    # Close the sockets as we don't need them any more.
    send_sock.close()
    bcast_sock.close()

    logging.info(str(len(modules_found)) + " modules found. " + str(len(response_list)) + " total responses heard.")
    return modules_found


def id_discover_lan(net_adapter_ip=None, num_attempts=2):
    # Apply limits to the num_attempts
    if num_attempts < 0:
        num_attempts = 1
    if num_attempts > 6:
        num_attempts = 6

    logging.info("discover_modules(), " + str(num_attempts) + " attempts.")
    all_modules_on_all_ifs = {}
    if net_adapter_ip is None:
        # netif_ip_list = NetIfs.get_network_interfaces_using_netifaces()
        netif_ip_list = _get_network_interfaces_using_ifaddr(one_ip_per_adapter=True)
    else:
        netif_ip_list = [(None, str(ipaddress.IPv4Address(net_adapter_ip)))]
    # Go over all network interfaces
    for netif_ip in netif_ip_list:
        logging.info("Discovering modules on " + netif_ip[1] + ":")
        modules_found = _discover_modules_on_netif(netif_ip, num_attempts, 0.2)
        # store the module info in the common dictionary
        try:
            for serial, mod_d in modules_found.items():
                if serial not in all_modules_on_all_ifs:
                    all_modules_on_all_ifs[serial] = mod_d
        except Exception:
            pass

    # Return a stripped down version of the dictionary because the serial number key is no longer needed.
    results = list(all_modules_on_all_ifs.values())
    logging.info(f"Total modules found: {len(results)}")
    return results
