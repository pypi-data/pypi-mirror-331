# JTAK
A [TAK](https://tak.gov) client.

JTAK provides a full-featured TAK client with multiple
input/outputs, Tak Protocol negotiation, state persistence
of discovered atoms and chat groups, and concise configuration.

Written in Python, it serves well for quick experimentation
and integration in a variety of environments.

> Note: You probably don't need to clone this repo. See [Integration](#integration)

## Install

```
pip install jtak
```

## Run

```
jtak_example
```

## Configuration

The example runs "out-of-the-box", but you'll likely want to
customize the configuration. A single configuration object holds
user and worker information.

By default you'll get a random `uid` each time, so setting that
is important if you plan to send cot messages. A `callsign` is
helpful as well.

If you don't specify any workers, you'll get the default set:
```py
[
    WorkerConf("udp://239.2.3.1:6969"),
    WorkerConf("udp://224.10.10.1:17012"),
    WorkerConf("tcp://0.0.0.0:4242")
]
```

If you do specify any workers, you'll need to specify *all* the
desired workers; consider adding the default workers in
addition to your others. Also note the `enabled` flag so you don't
have to delete them to make changes...you can
maintain a list of workers and disable any with that flag.

```py
ClientConf(
    user=UserConf(
        uid="some-unique-id-1234567890",
        callsign="ENDER"
    ),
    workers=[
        WorkerConf(
            url="tls://192.168.1.99:8089",
            tls_hostname="tak.local",
            tls_p12_path="cyan.p12",
            tls_p12_password="atakatak"
        ),
        WorkerConf("stcp://192.168.1.99:8088", enabled=False)
    ],
    sa_interval=30
)
```

### ClientConf
Field       | Default | Notes
-----       | ------- | -----
user        | default | see UserConf
workers     | default | see WorkerConf
sa_interval | 30.0    | send device beacon at this interval (0 for no beacon)

### UserConf
Field      | Default         | Notes
-----      | -------         | -----
uid        | "jtak-{random}" | unique and persistent user id
callsign   | ""              | ATAK display name
cot_type   | "a-f-G"         | ATAK marker type
team       | "Cyan"          |
role       | "Team Member"   |
lat        | 0.0             | initial latitude
lon        | 0.0             | initial longitude
hae        | 0.0             | initial altitude

### WorkerConf
Field     | Default | Notes
-----     | ------- | -----
url       | ""      | scheme://host:port (where scheme is "udp", "tcp", "tls")
enabled   | True    | ignore if False
legacy    | False   | force tak proto 0 (legacy)
username  | ""      | tak server creds
password  | ""      | tak server creds
local_ip  | ""      | local ip or adapter name; if blank, uses first of wifi, eth, lo
tx_delay  | 0.0     | some tak servers might require a slight delay between cot message (negative value produces random values between 0 and abs(tx_delay))
mesh_ttl  | 1       | time-to-live for multicast transmissions
mesh_mode | "rw"    | A mesh worker can be read, write or both
tls       | default | see TLSConfig

### TLSConf
Field             | Default    | Notes
-----             | -------    | -----
hostname          | ""         | tls server hostname for certificate verification (helpful when url specifies ip address or different name than in server certificate)
ciphers           | "ALL"      | use to filter tls ciphers
p12_path          | ""         | path to client certificate p12 file
p12_password      | "atakatak" | password to client certificate p12 file (Hopefully you have to specify this! :joy:)
skip_verification | False      | skip tak server certificate verification (Hopefully this is only enabled for testing! But you'll probably have to enable this because TakServer's certificate includes the CA certificate by default, which is frowned upon by verification tools. :grimace:)

## Integration

`jtak` implements the core messaging protocol, but unless you just
want to watch message traffic in a terminal, you will want to write
a wrapper for it.

In your own project, inherit `TakClient` and implement the desired abstract methods.

```py
import jtak

class MyTakClient(jtak.TakClient):

    def sa_cot(self, endpoint: str):
        # Override this if you want a custom SA message.
        # Otherwise just keep self.me updated and SA messages are sent.
        # see `jtak.cot.default_sa_cot` as an example
        cot = ...
        return cot

    async def _inbound_handler(cot: CotEvent):
        # Override this if your inbound consumer wants something
        # other than a protobuf CotEvent message.

        # do something with cot
        # state is available in self.state if needed
        # returned objects are enqueued for an inbound bridge consumer
        return model

    async def outbound(self, model):
        # Override this if your outbound provider doesn't
        # produce COT messages.

        # convert the model into cot message(s)
        # or process model (ie. update self.me) and return None
        # returned cot messages are enqueued for outbound transmission
        return super().outbound(messages)
```

## Runner

```
                    TakClient
                ┌ --------------- ┐
        ---->   | outbound(model) | tx ----->
Runner/Bridge   |                 |       Network
        <----   | inbound()       | rx <-----
                └ --------------- ┘
```

A Runner is an application you write that instantiates a TakClient
and runs it, as well as provides some means of pushing and pulling
messages.

See `jtak_example.py` for a simple runner. It simply runs the TakClient
with a logging level to see activity; it doesn't process messages.

If your data generation or processing integrates nicely with asyncio
tasks, you can likely simply extend `jtak_example.py`.

However, if data generation or processing is more complex or running in
a different process or application, you may need to implement a
bridge. A bridge might itself send and receive messages
between it and another application or process by various means
like message queues.

## Contributing
We are happy to support any community of interest that grows around jtak.
However, we are (overly) opinionated, so it's a good idea to run an idea by us before putting significant effort into a PR.

And really, jtak shouldn't change too much. Specific use cases can inherit from jtak to add cool custom functionality.

## Development

As mentioned earlier, COT messages can be structured as XML or Protobuf. Although XML is "legacy", it is required that all clients support XML for the time being.

Internally, `jtak` uses a mix of the two. Inbound messages are coverted to TakMessages (protobuf) regardless of how they are received. However, "non-standard" detail is included in an "xmlDetail" field, so even with TakMessage some xml processing may still be required.

Outbound messages are sent in accordance with the current tak protocol negotation; a client shouldn't send protobuf until its negotiation allows. However, `jtak` *generates* messages as XML (e.g. the default sa cot message).

In short `jtak` prefers to construct messages as XML and process messages as protobuf.

## Acknowledgements

Inspired by the great work at https://github.com/snstac.
