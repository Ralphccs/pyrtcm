# pyrtcm

[Current Status](#currentstatus) |
[Installation](#installation) |
[Reading](#reading) |
[Parsing](#parsing) |
[Generating](#generating) |
[Serializing](#serializing) |
[Examples](#examples) |
[Extensibility](#extensibility) |
[Graphical Client](#gui) |
[Author & License](#author)

`pyrtcm` is an original Python 3 library for the RTCM3 &copy; GPS/GNSS protocol, or more properly
the "RTCM STANDARD 10403.n DIFFERENTIAL GNSS (GLOBAL NAVIGATION SATELLITE SYSTEMS) SERVICES – VERSION 3".

RTCM3 is a proprietary GPS/GNSS protocol published by the Radio Technical Commission for Maritime Services.

The `pyrtcm` homepage is located at [https://github.com/semuconsulting/pyrtcm](https://github.com/semuconsulting/pyrtcm).

This is an independent project and we have no affiliation whatsoever with the Radio Technical Commission for Maritime Services.

**FYI** There are companion libraries which handle standard NMEA 0183 &copy; and UBX &copy; (u-blox) GNSS/GPS messages:
- [pynmeagps](http://github.com/semuconsulting/pynmeagps)
- [pyubx2](http://github.com/semuconsulting/pyubx2)

## <a name="currentstatus">Current Status</a>

<!--![Status](https://img.shields.io/pypi/status/pyrtcm)-->
![Release](https://img.shields.io/github/v/release/semuconsulting/pyrtcm?include_prereleases)
![Build](https://img.shields.io/github/workflow/status/semuconsulting/pyrtcm/pyrtcm)
![Codecov](https://img.shields.io/codecov/c/github/semuconsulting/pyrtcm)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/pyrtcm)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/pyrtcm)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/pyrtcm.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/pyrtcm)

Currently in development. Refer to the `RTCM_PAYLOADS_GET` dictionary in `rtcmtypes_get.py` for a list of message types currently implemented (*but not necessarily tested*). Additional message types can be readily added - see [Extensibility](#extensibility)).

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pyrtcm](https://www.semuconsulting.com/pyrtcm).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/pyrtcm/blob/master/CONTRIBUTING.md).

[Bug reports](https://github.com/semuconsulting/pyrtcm/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/pyrtcm/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided.

---
## <a name="installation">Installation</a>

`pyrtcm` is compatible with Python 3.6+ and has no third-party library dependencies.

In the following, `python` & `pip` refer to the Python 3 executables. You may need to type 
`python3` or `pip3`, depending on your particular environment.

![Python version](https://img.shields.io/pypi/pyversions/pyrtcm.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/pyrtcm.svg?style=flat)](https://pypi.org/project/pyrtcm/)
![PyPI downloads](https://img.shields.io/pypi/dm/pyrtcm.svg?style=flat)

The recommended way to install the latest version of `pyrtcm` is with
[pip](http://pypi.python.org/pypi/pip/):

```shell
python -m pip install --upgrade pyrtcm
```

Local installation is also available, provided you have the Python packages `setuptools` and `wheel` installed:

```shell
git clone https://github.com/semuconsulting/pyrtcm.git
cd pyrtcm
python setup.py sdist bdist_wheel
python -m pip install dist/pyrtcm-0.1.3.tar.gz --user --force_reinstall
```

---
## <a name="reading">Reading (Streaming)</a>

```
class pyrtcm.rtcmreader.RTCMReader(stream, **kwargs)
```

You can create a `RTCMReader` object by calling the constructor with an active stream object. 
The stream object can be any data stream which supports a `read(n) -> bytes` method (e.g. File or Serial, with 
or without a buffer wrapper).

Individual RTCM messages can then be read using the `RTCMReader.read()` function, which returns both the raw binary data (as bytes) and the parsed data (as a `RTCMMessage`, via the `parse()` method). The function is thread-safe in so far as the incoming data stream object is thread-safe. `RTCMReader` also implements an iterator.

Example -  Serial input:
```python
>>> from serial import Serial
>>> from pyrtcm import RTCMReader
>>> stream = Serial('/dev/tty.usbmodem14101', 9600, timeout=3)
>>> rtr = RTCMReader(stream)
>>> (raw_data, parsed_data) = rtr.read()
>>> print(parsed_data)
```

Example - File input (using iterator).
```python
>>> from pyrtcm import RTCMReader
>>> stream = open('rtcmdata.log', 'rb')
>>> rtr = RTCMReader(stream)
>>> for (raw_data, parsed_data) in rtr: print(parsed_data)
...
```

---
## <a name="parsing">Parsing</a>

You can parse individual RTCM messages using the static `RTCMReader.parse(data)` function, which takes a bytes array containing a binary RTCM message payload and returns a `RTCMMessage` object.

**NB:** Once instantiated, an `RTCMMessage` object is immutable.

Example:
```python
>>> from pyrtcm import RTCMReader
>>> msg = RTCMReader.parse(b"\xd3\x00\x13>\xd0\x00\x03\x8aX\xd9I<\x87/4\x10\x9d\x07\xd6\xafH Z\xd7\xf7")
>>> print(msg)
<RTCM(1005, DF002=1005, DF003=0, DF021=0, DF022=1, DF023=1, DF024=1, DF141=0, DF025=44440308028, DF142=1, DF001_1=0, DF026=30856712349, DF364=0, DF027=33666582560)>
```

The `RTCMMessage` object exposes different public attributes depending on its message type or 'identity'. Attributes are defined as data fields ("DF002", "DF003", etc.) e.g. the `1005` message contains the following dasa fields:

```python
>>> print(msg)
<RTCM(1005, DF002=1005, DF003=0, DF021=0, DF022=1, DF023=1, DF024=1, DF141=0, DF025=44440308028, DF142=1, DF001_1=0, DF026=30856712349, DF364=0, DF027=33666582560)>
>>> msg.identity
'1005'
>>> msg.DF024
1
```

A helper method `datadesc(datafield)` is available to convert a data field to a descriptive string,
e.g. "DF004" -> "GPS Epoch Time (TOW)"

Attributes within repeating groups are parsed with a two-digit suffix (DF030_01, DF030_02, etc.). The `payload` attribute always contains the raw payload as bytes.

---
## <a name="generating">Generating</a>

```
class pyrtcm.rtcmmessage.RTCMMessage(payload, **kwargs)
```

You can create an `RTCMMessage` object by calling the constructor with the following parameters:
1. payload as bytes

Example:

```python
>>> from pyrtcm import RTCMMessage
>>> msg = RTCMMessage(b">\xd0\x00\x03\x8aX\xd9I<\x87/4\x10\x9d\x07\xd6\xafH ")
>>> print(msg)
<RTCM(1005, DF002=1005, DF003=0, DF021=0, DF022=1, DF023=1, DF024=1, DF141=0, DF025=44440308028, DF142=1, DF001_1=0, DF026=30856712349, DF364=0, DF027=33666582560)>
```

---
## <a name="serializing">Serializing</a>

The `RTCMMessage` class implements a `serialize()` method to convert a `RTCMMessage` object to a bytes array suitable for writing to an output stream.

e.g. to create and send a `1005` message type:

```python
>>> from serial import Serial
>>> serialOut = Serial('COM7', 38400, timeout=5)
>>> from pyrtcm import RTCMMessage
>>> msg = RTCMMessage(b">\xd0\x00\x03\x8aX\xd9I<\x87/4\x10\x9d\x07\xd6\xafH ")
>>> print(msg)
<RTCM(1005, DF002=1005, DF003=0, DF021=0, DF022=1, DF023=1, DF024=1, DF141=0, DF025=44440308028, DF142=1, DF001_1=0, DF026=30856712349, DF364=0, DF027=33666582560)>
>>> output = msg.serialize()
>>> output
b'\xd3\x00\x13>\xd0\x00\x03\x8aX\xd9I<\x87/4\x10\x9d\x07\xd6\xafH Z\xd7\xf7'
>>> serialOut.write(output)
```

---
## <a name="examples">Examples</a>

The following examples are available in the /examples folder:

1. `rtcmfile.py` - stream RTCM data from binary log file.
2. `rtcmserial.py` - stream RTCM data from serial/UART port.
3. `rtcmbuild.py` - construct RTCM payload from constituent datafields.

---
## <a name="extensibility">Extensibility</a>

The RTCM protocol is principally defined in the modules `rtcmtypes_core.py` and `rtcmtypes_get.py` as a series of dictionaries. RTCM uses a series of pre-defined data fields ("DF002", DF003" etc.), each of which has a designated data type (UINT32, etc.). Message payload definitions must conform to the following rules:

```
1. attribute names must be unique within each message class
2. attribute types must be one of the valid data fields (DF026, DF059, etc.)
3. repeating or bitfield groups must be defined as a tuple ('numr', {dict}), where:
   'numr' is either:
     a. an integer representing a fixed number of repeats e.g. 32
     b. a string representing the name of a preceding attribute containing the number of repeats e.g. 'DF029'
   {dict} is the nested dictionary of repeating items or bitfield group
```

Repeating attribute names are parsed with a two-digit suffix (DF030_01, DF030_02, etc.). Nested repeating groups are supported.

---
## <a name="cli">Command Line Utility</a>

TODO

---
## <a name="gui">Graphical Client</a>

A python/tkinter graphical GPS client which supports NMEA, UBX and RTCM protocols is available at: 

[https://github.com/semuconsulting/PyGPSClient](https://github.com/semuconsulting/PyGPSClient)

---
## <a name="author">Author & License Information</a>

semuadmin@semuconsulting.com

![License](https://img.shields.io/github/license/semuconsulting/pyrtcm.svg)

`pyrtcm` is maintained entirely by volunteers. If you find it useful, a small donation would be greatly appreciated!

[![Donations](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=4TG5HGBNAM7YJ)
