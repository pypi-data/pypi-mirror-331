
# FIPS-205 SLH-DSA bindings for botan3

The [botan](https://botan.randombit.net/) cryptographic library
implements NIST's
[FIP-205](https://csrc.nist.gov/pubs/fips/205/final)
[SLH-DSA](https://botan.randombit.net/doxygen/group__sphincsplus__common.html)
signature algorithm, using the `botan3`
[python bindings](https://botan.randombit.net/handbook/api_ref/python.html).

This wraps these bindings to help usage of SLH-DSA in python:

```py
from slh_dsa_botan3 import slh_params

slh_dsa = slh_params()

private_key = slh_dsa.generate_keypair()
public_key = private_key.get_public_key()

message = "hello world"
signature = private_key.sign(message)

assert public_key.verify(message, signature)
```

## Quick setup

You need a working `botan3` installation:

```sh
% botan --version
3.7.1
```

You may need to install `python3-botan` depending on your distribution:

```sh
% python -c 'import botan3; print(botan3.version_string())'
Botan 3.7.1 (release, dated 20250205, revision git:09cc7f97ceb828c19461b2a63f820d3226bb921b, distribution unspecified)
```

It is recommended to work in a virtual environment as follows:

```sh
% python3 -m venv --system-site-packages botan3 venv
% source venv/bin/activate
```

You can then install `slh_dsa_botan3` using the following:

```sh
% pip install slh_dsa_botan3
```

Note that this is still experimental and may include mistakes, use with care!
