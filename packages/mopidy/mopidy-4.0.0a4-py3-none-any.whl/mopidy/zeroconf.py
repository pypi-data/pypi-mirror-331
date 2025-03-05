import logging
import string

logger = logging.getLogger(__name__)

try:
    import dbus  # pyright: ignore[reportMissingImports]
except ImportError:
    dbus = None

_AVAHI_IF_UNSPEC = -1
_AVAHI_PROTO_UNSPEC = -1
_AVAHI_PUBLISHFLAGS_NONE = 0


def _is_loopback_address(host: str) -> bool:
    return host.startswith(("127.", "::ffff:127.")) or host == "::1"


def _convert_text_list_to_dbus_format(text_list: list[str]):
    assert dbus
    array = dbus.Array(signature="ay")
    for text in text_list:
        array.append([dbus.Byte(ord(c)) for c in text])
    return array


class Zeroconf:
    """Publish a network service with Zeroconf.

    Currently, this only works on Linux using Avahi via D-Bus.

    :param str name: human readable name of the service, e.g. 'MPD on neptune'
    :param str stype: service type, e.g. '_mpd._tcp'
    :param int port: TCP port of the service, e.g. 6600
    :param str domain: local network domain name, defaults to ''
    :param str host: interface to advertise the service on, defaults to ''
    :param text: extra information depending on ``stype``, defaults to empty
        list
    :type text: list of str
    """

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        stype: str,
        port: int,
        domain: str = "",
        host: str = "",
        text: list[str] | None = None,
    ) -> None:
        self.stype = stype
        self.port = port
        self.domain = domain
        self.host = host
        self.text = text or []

        self.bus = None
        self.server = None
        self.group = None
        self.display_hostname = None
        self.name = None

        if dbus:
            try:
                self.bus = dbus.SystemBus()
                self.server = dbus.Interface(
                    self.bus.get_object("org.freedesktop.Avahi", "/"),
                    "org.freedesktop.Avahi.Server",
                )
                self.display_hostname = f"{self.server.GetHostName()}"
                self.name = string.Template(name).safe_substitute(
                    hostname=self.display_hostname,
                    port=port,
                )
            except dbus.exceptions.DBusException as e:
                logger.debug("%s: Server failed: %s", self, e)

    def __str__(self) -> str:
        return (
            f"Zeroconf service {self.name!r} "
            f"({self.stype} at [{self.host}]:{self.port:d})"
        )

    def publish(self) -> bool:  # noqa: PLR0911
        """Publish the service.

        Call when your service starts.
        """
        if _is_loopback_address(self.host):
            logger.debug("%s: Publish on loopback interface is not supported.", self)
            return False

        if not dbus:
            logger.debug("%s: dbus not installed; publish failed.", self)
            return False

        if not self.bus:
            logger.debug("%s: Bus not available; publish failed.", self)
            return False

        if not self.server:
            logger.debug("%s: Server not available; publish failed.", self)
            return False

        try:
            if not self.bus.name_has_owner("org.freedesktop.Avahi"):
                logger.debug("%s: Avahi service not running; publish failed.", self)
                return False

            self.group = dbus.Interface(
                self.bus.get_object(
                    "org.freedesktop.Avahi",
                    self.server.EntryGroupNew(),
                ),
                "org.freedesktop.Avahi.EntryGroup",
            )

            self.group.AddService(
                _AVAHI_IF_UNSPEC,
                _AVAHI_PROTO_UNSPEC,
                dbus.UInt32(_AVAHI_PUBLISHFLAGS_NONE),
                self.name,
                self.stype,
                self.domain,
                self.host,
                dbus.UInt16(self.port),
                _convert_text_list_to_dbus_format(self.text),
            )

            self.group.Commit()
            logger.debug("%s: Published", self)
        except dbus.exceptions.DBusException as e:
            logger.debug("%s: Publish failed: %s", self, e)
            return False
        else:
            return True

    def unpublish(self) -> None:
        """Unpublish the service.

        Call when your service shuts down.
        """
        if not dbus or not self.group:
            return

        try:
            self.group.Reset()
            logger.debug("%s: Unpublished", self)
        except dbus.exceptions.DBusException as e:
            logger.debug("%s: Unpublish failed: %s", self, e)
        finally:
            self.group = None
