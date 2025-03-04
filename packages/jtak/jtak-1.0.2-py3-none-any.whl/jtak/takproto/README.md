# TakProto

A Python module for handling Tak Protocol and cursor-on-target (COT) messages used with [TAK Products](https://www.tak.gov/).

COT messages can be structured as either an XML Element (legacy)
or protobuf TakMessage.

This module provides functions for converting between those structures
as well as serializing and deserializing both the header and message.


## Origin

The `proto` folder is a local copy of the publicly available source at https://github.com/deptofdefense/AndroidTacticalAssaultKit-CIV/tree/main/takproto. See the README.md at that link for a description of the tak protocol.

This module is a significant rewrite of [snstac takproto](https://github.com/snstac/takproto)
which was forked from (and now merged back into) [db-SPL takproto](https://github.com/dB-SPL/takprotobuf).

To honor their MIT license, it is included in [ThirdPartyLicense.md](ThirdPartyLicense.md).
