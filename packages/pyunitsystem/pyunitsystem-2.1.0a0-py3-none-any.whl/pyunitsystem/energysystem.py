from pyunitsystem.unit import Unit

# Constants
_elementary_charge_coulomb = 1.602176634e-19


_joule_si = 1.0


class EnergySI(Unit):
    """Util enum for energy in SI units (Joules)"""

    JOULE = _joule_si
    ELEMCHARGE = _elementary_charge_coulomb
    ELECTRONVOLT = _elementary_charge_coulomb

    KILOELECTRONVOLT = _elementary_charge_coulomb * 1e3
    MEGAELECTRONVOLT = _elementary_charge_coulomb * 1e6
    GIGAELECTRONVOLT = _elementary_charge_coulomb * 1e9
    KILOJOULE = 1e3 * _joule_si

    @classmethod
    def from_str(cls, value: str):
        if value.lower() in ("j", "joule"):
            return EnergySI.JOULE
        elif value.lower() in ("kj", "kilojoule"):
            return EnergySI.KILOJOULE
        elif value.lower() in ("ev", "electronvolt"):
            return EnergySI.ELECTRONVOLT
        elif value.lower() in ("kev", "kiloelectronvolt"):
            return EnergySI.KILOELECTRONVOLT
        elif value.lower() in ("mev", "megaelectronvolt"):
            return EnergySI.MEGAELECTRONVOLT
        elif value.lower() in ("gev", "gigaelectronvolt"):
            return EnergySI.GIGAELECTRONVOLT
        elif value.lower() in ("e", "qe"):
            return EnergySI.ELEMCHARGE
        else:
            raise ValueError(f"Cannot convert: {value}")

    def __str__(self):
        if self is EnergySI.JOULE:
            return "J"
        elif self is EnergySI.KILOJOULE:
            return "kJ"
        elif self is EnergySI.ELECTRONVOLT:
            return "eV"
        elif self is EnergySI.KILOELECTRONVOLT:
            return "keV"
        elif self is EnergySI.MEGAELECTRONVOLT:
            return "meV"
        elif self is EnergySI.GIGAELECTRONVOLT:
            return "geV"
        elif self is EnergySI.ELEMCHARGE:
            # in fact will never be called because
            # EnergySI.ELEMCHARGE is EnergySI.ELECTRONVOLT
            return "e"
