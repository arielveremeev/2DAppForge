import os
import sys
import argparse
from OpenSSL import crypto
import socket
import ipaddress


def generate_self_signed_certificate(cert_file, key_file, cn='192.168.0.60'):
    """
        The generate_self_signed_certificate function is used to create a self-signed certificate and a private key,
        and then write them to files. The function takes three parameters: cert_file, key_file, and cn (Common Name), which4 defaults to '192.168.0.60'.
        The function begins by generating a new RSA key pair with a key size of 2048 bits.
        This is done using the crypto.PKey() function to create a new key object, and then calling the generate_key method on this object.
        at the end of the function, the certificate and private key are written to files using the dump_certificate and dump_privatekey functions.
    """

    # Generate a new key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed certificate
    cert = crypto.X509()
    cert.get_subject().CN = cn
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    # Write the certificate and private key to files
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", help="Directory to put certificates")
    args = parser.parse_args()

    cert_file = "server.crt"
    key_file = "server.key"

    if args.outdir:
        os.makedirs(args.outdir, exist_ok=True)
        cert_file = os.path.join(args.outdir, cert_file)
        key_file = os.path.join(args.outdir, key_file)

    # Get the IP address of the host
    ip_address = socket.gethostbyname(socket.gethostname())
    ip_address = ipaddress.ip_address(ip_address)

    generate_self_signed_certificate(cert_file, key_file, cn=str(ip_address))
    print(f"Certificate and key generated successfully for IP: {ip_address}")
