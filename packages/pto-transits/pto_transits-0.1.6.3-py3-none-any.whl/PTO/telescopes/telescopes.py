from . import instruments
import astropy.coordinates as coord
import astropy.units as u
import numpy as np
from dataclasses import dataclass, field
import logging
from ..utils.utilities import logger_default
from .telescope_config import TELESCOPE_CONFIGS

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger = logger_default(logger)


@dataclass
class Telescope():
    name: str
    location: coord.earth.EarthLocation
    instruments: list = field(default_factory=list)
    diameter: u.Quantity = 0 * u.m,
    operational: bool = True,
    variable_name: str = ''

    def telescope_constraints(self, Event):
        logger.warning('Telescope constraints not implemented yet.')
        return

    def zenith_constraints(self, Event):
        logger.warning('Telescope zenith constraints not implemented yet.')
        return


class SwissEulerTelescope(Telescope):
    pass


SwissEuler = SwissEulerTelescope(
    name='Swiss Euler Telescope',
    location=coord.EarthLocation.of_site('La Silla Observatory'),
    instruments=[instruments.CORALIE],
    diameter=1.2 * u.m
)


class LaSilla36mTelescope(Telescope):
    pass


LaSilla3_6m = LaSilla36mTelescope(
    name='ESO 3.6m Telescope (La Silla)',
    location=coord.EarthLocation.of_site('La Silla Observatory (ESO)'),
    instruments=[instruments.HARPS, instruments.NIRPS],
    diameter=3.6 * u.m
)


class VLTTelescope(Telescope):
    pass


VLT = VLTTelescope(
    name='Very Large Telescope (VLT)',
    location=coord.EarthLocation.of_site('Paranal'),
    instruments=[instruments.ESPRESSO, instruments.UVES],
    diameter=8.2 * u.m
)


class VLT4UTTelescope(Telescope):
    pass


VLT_4UT = VLT4UTTelescope(
    name='Very Large Telescope (VLT) 4-UT',
    location=coord.EarthLocation.of_site('Paranal'),
    instruments=[instruments.ESPRESSO_4UT],
    diameter=2 * 8.2 * u.m  # Combined light from all 4 UTs
)


class LowellDiscoveryTelescope(Telescope):
    pass


LowellDiscovery = LowellDiscoveryTelescope(
    name='Lowell Discovery Telescope',
    location=coord.EarthLocation.of_site('Lowell Observatory'),
    instruments=[instruments.EXPRES],
    diameter=4.3 * u.m
)


class TNGTelescope(Telescope):
    pass


TNG = TNGTelescope(
    name='Telescopio Nazionale Galileo (TNG)',
    location=coord.EarthLocation.of_site('Roque de los Muchachos'),
    instruments=[instruments.GIANO, instruments.HARPS_N],
    diameter=3.58 * u.m
)


class GeminiNorthTelescope(Telescope):
    pass


GeminiNorth = GeminiNorthTelescope(
    name='Gemini North Telescope',
    location=coord.EarthLocation.of_site('gemini_north'),
    instruments=[instruments.MAROON_X],
    diameter=8.1 * u.m
)


class CFHTTelescope(Telescope):
    pass


CFHT = CFHTTelescope(
    name='Canada-France-Hawaii Telescope (CFHT)',
    location=coord.EarthLocation.of_site('Canada-France-Hawaii Telescope'),
    instruments=[instruments.SPIROU],
    diameter=3.6 * u.m
)


class HauteProvenceTelescope(Telescope):
    pass


HauteProvence = HauteProvenceTelescope(
    name='Haute-Provence Observatory',
    location=coord.EarthLocation.of_site('Observatoire de Haute Provence'),
    instruments=[instruments.SOPHIE],
    diameter=1.93 * u.m
)


class CalarAltoObservatory(Telescope):
    pass


CalarAlto = CalarAltoObservatory(
    name='Calar Alto Observatory',
    location=coord.EarthLocation.of_site('Observatorio de Calar Alto'),
    instruments=[instruments.CARMENES],
    diameter=3.5 * u.m
)


class TelescopeFactory:
    @staticmethod
    def create_telescope(telescope_type: str) -> Telescope:
        """Create a telescope instance based on the telescope type."""
        if telescope_type not in TELESCOPE_CONFIGS:
            raise ValueError(f"Unknown telescope type: {telescope_type}")

        config = TELESCOPE_CONFIGS[telescope_type]
        return Telescope(
            name=config['name'],
            location=coord.EarthLocation.of_site(config['location']),
            instruments=config['instruments'],
            diameter=config['diameter']
        )


aao = TelescopeFactory.create_telescope('AAO')
allen_telescope_array = TelescopeFactory.create_telescope(
    'ALLEN_TELESCOPE_ARRAY')
alma = TelescopeFactory.create_telescope('ALMA')
anderson_mesa = TelescopeFactory.create_telescope('ANDERSON_MESA')
anglo_australian_observatory = TelescopeFactory.create_telescope(
    'ANGLO_AUSTRALIAN_OBSERVATORY')
ao = TelescopeFactory.create_telescope('AO')
apache_point = TelescopeFactory.create_telescope('APACHE_POINT')
apache_point_observatory = TelescopeFactory.create_telescope(
    'APACHE_POINT_OBSERVATORY')
apo = TelescopeFactory.create_telescope('APO')
arca = TelescopeFactory.create_telescope('ARCA')
arecibo = TelescopeFactory.create_telescope('ARECIBO')
arecibo_observatory = TelescopeFactory.create_telescope('ARECIBO_OBSERVATORY')
askap = TelescopeFactory.create_telescope('ASKAP')
astroparticle_research_with_cosmics_in_the_abyss = TelescopeFactory.create_telescope(
    'ASTROPARTICLE_RESEARCH_WITH_COSMICS_IN_THE_ABYSS')
ata = TelescopeFactory.create_telescope('ATA')
atacama_large_millimeter_array = TelescopeFactory.create_telescope(
    'ATACAMA_LARGE_MILLIMETER_ARRAY')
atst = TelescopeFactory.create_telescope('ATST')
australian_square_kilometre_array_pathfinder = TelescopeFactory.create_telescope(
    'AUSTRALIAN_SQUARE_KILOMETRE_ARRAY_PATHFINDER')
bao = TelescopeFactory.create_telescope('BAO')
bbso = TelescopeFactory.create_telescope('BBSO')
beijing_xinglong_observatory = TelescopeFactory.create_telescope(
    'BEIJING_XINGLONG_OBSERVATORY')
big_bear_solar_observatory = TelescopeFactory.create_telescope(
    'BIG_BEAR_SOLAR_OBSERVATORY')
black_moshannon_observatory = TelescopeFactory.create_telescope(
    'BLACK_MOSHANNON_OBSERVATORY')
bmo = TelescopeFactory.create_telescope('BMO')
caha = TelescopeFactory.create_telescope('CAHA')
canada_france_hawaii_telescope = TelescopeFactory.create_telescope(
    'CANADA_FRANCE_HAWAII_TELESCOPE')
canadian_hydrogen_intensity_mapping_experiment = TelescopeFactory.create_telescope(
    'CANADIAN_HYDROGEN_INTENSITY_MAPPING_EXPERIMENT')
catalina_observatory = TelescopeFactory.create_telescope(
    'CATALINA_OBSERVATORY')
catalina_observatory: _61_inch_telescope = TelescopeFactory.create_telescope(
    'CATALINA_OBSERVATORY:_61_INCH_TELESCOPE')
centro_astronomico_hispano_aleman, _almeria = TelescopeFactory.create_telescope(
    'CENTRO_ASTRONOMICO_HISPANO_ALEMAN,_ALMERIA')
cerro_armazones_observatory = TelescopeFactory.create_telescope(
    'CERRO_ARMAZONES_OBSERVATORY')
cerro_pachon = TelescopeFactory.create_telescope('CERRO_PACHON')
cerro_paranal = TelescopeFactory.create_telescope('CERRO_PARANAL')
cerro_tololo = TelescopeFactory.create_telescope('CERRO_TOLOLO')
cerro_tololo_interamerican_observatory = TelescopeFactory.create_telescope(
    'CERRO_TOLOLO_INTERAMERICAN_OBSERVATORY')
cfht = TelescopeFactory.create_telescope('CFHT')
chara = TelescopeFactory.create_telescope('CHARA')
chime = TelescopeFactory.create_telescope('CHIME')
cima_ekar_182_cm_telescope = TelescopeFactory.create_telescope(
    'CIMA_EKAR_182_CM_TELESCOPE')
cima_ekar_observing_station = TelescopeFactory.create_telescope(
    'CIMA_EKAR_OBSERVING_STATION')
ctio = TelescopeFactory.create_telescope('CTIO')
daniel_k__inouye_solar_telescope = TelescopeFactory.create_telescope(
    'DANIEL_K._INOUYE_SOLAR_TELESCOPE')
dao = TelescopeFactory.create_telescope('DAO')
dct = TelescopeFactory.create_telescope('DCT')
discovery_channel_telescope = TelescopeFactory.create_telescope(
    'DISCOVERY_CHANNEL_TELESCOPE')
dkist = TelescopeFactory.create_telescope('DKIST')
dominion_astrophysical_observatory = TelescopeFactory.create_telescope(
    'DOMINION_ASTROPHYSICAL_OBSERVATORY')
dominion_radio_astrophysical_observatory = TelescopeFactory.create_telescope(
    'DOMINION_RADIO_ASTROPHYSICAL_OBSERVATORY')
drao = TelescopeFactory.create_telescope('DRAO')
drao_26m_telescope = TelescopeFactory.create_telescope('DRAO_26M_TELESCOPE')
effelsberg = TelescopeFactory.create_telescope('EFFELSBERG')
effelsberg_100_m_radio_telescope = TelescopeFactory.create_telescope(
    'EFFELSBERG_100_M_RADIO_TELESCOPE')
ekar = TelescopeFactory.create_telescope('EKAR')
example_site = TelescopeFactory.create_telescope('EXAMPLE_SITE')
fast = TelescopeFactory.create_telescope('FAST')
five_hundred_meter_aperture_spherical_radio_telescope = TelescopeFactory.create_telescope(
    'FIVE_HUNDRED_METER_APERTURE_SPHERICAL_RADIO_TELESCOPE')
flwo = TelescopeFactory.create_telescope('FLWO')
g1 = TelescopeFactory.create_telescope('G1')
gbt = TelescopeFactory.create_telescope('GBT')
gemini_north = TelescopeFactory.create_telescope('GEMINI_NORTH')
gemini_south = TelescopeFactory.create_telescope('GEMINI_SOUTH')
gemn = TelescopeFactory.create_telescope('GEMN')
gems = TelescopeFactory.create_telescope('GEMS')
geo = TelescopeFactory.create_telescope('GEO')
geo600_gravitational_wave_detector = TelescopeFactory.create_telescope(
    'GEO600_GRAVITATIONAL_WAVE_DETECTOR')
geo_600 = TelescopeFactory.create_telescope('GEO_600')
giant_metrewave_radio_telescope = TelescopeFactory.create_telescope(
    'GIANT_METREWAVE_RADIO_TELESCOPE')
gmrt = TelescopeFactory.create_telescope('GMRT')
greenwich = TelescopeFactory.create_telescope('GREENWICH')
green_bank_observatory = TelescopeFactory.create_telescope(
    'GREEN_BANK_OBSERVATORY')
green_bank_telescope = TelescopeFactory.create_telescope(
    'GREEN_BANK_TELESCOPE')
h1 = TelescopeFactory.create_telescope('H1')
haleakala = TelescopeFactory.create_telescope('HALEAKALA')
haleakala_observatories = TelescopeFactory.create_telescope(
    'HALEAKALA_OBSERVATORIES')
hale_telescope = TelescopeFactory.create_telescope('HALE_TELESCOPE')
halo = TelescopeFactory.create_telescope('HALO')
happy_jack = TelescopeFactory.create_telescope('HAPPY_JACK')
hat_creek = TelescopeFactory.create_telescope('HAT_CREEK')
hat_creek_radio_observatory = TelescopeFactory.create_telescope(
    'HAT_CREEK_RADIO_OBSERVATORY')
hcro = TelescopeFactory.create_telescope('HCRO')
helium_and_lead_observatory = TelescopeFactory.create_telescope(
    'HELIUM_AND_LEAD_OBSERVATORY')
het = TelescopeFactory.create_telescope('HET')
hobby_eberly_telescope = TelescopeFactory.create_telescope(
    'HOBBY_EBERLY_TELESCOPE')
hyperk = TelescopeFactory.create_telescope('HYPERK')
hyper_kamiokande = TelescopeFactory.create_telescope('HYPER_KAMIOKANDE')
iao = TelescopeFactory.create_telescope('IAO')
icecube = TelescopeFactory.create_telescope('ICECUBE')
icecube_neutrino_observatory = TelescopeFactory.create_telescope(
    'ICECUBE_NEUTRINO_OBSERVATORY')
indian_astronomical_observatory = TelescopeFactory.create_telescope(
    'INDIAN_ASTRONOMICAL_OBSERVATORY')
irtf = TelescopeFactory.create_telescope('IRTF')
james_clerk_maxwell_telescope = TelescopeFactory.create_telescope(
    'JAMES_CLERK_MAXWELL_TELESCOPE')
jansky_very_large_array = TelescopeFactory.create_telescope(
    'JANSKY_VERY_LARGE_ARRAY')
jcmt = TelescopeFactory.create_telescope('JCMT')
john_galt_telescope = TelescopeFactory.create_telescope('JOHN_GALT_TELESCOPE')
k1 = TelescopeFactory.create_telescope('K1')
kagra = TelescopeFactory.create_telescope('KAGRA')
kamioka_gravitational_wave_detector = TelescopeFactory.create_telescope(
    'KAMIOKA_GRAVITATIONAL_WAVE_DETECTOR')
keck = TelescopeFactory.create_telescope('KECK')
keck_observatory = TelescopeFactory.create_telescope('KECK_OBSERVATORY')
kitt_peak = TelescopeFactory.create_telescope('KITT_PEAK')
kitt_peak_national_observatory = TelescopeFactory.create_telescope(
    'KITT_PEAK_NATIONAL_OBSERVATORY')
km3net_arca = TelescopeFactory.create_telescope('KM3NET_ARCA')
km3net_orca = TelescopeFactory.create_telescope('KM3NET_ORCA')
kpno = TelescopeFactory.create_telescope('KPNO')
l1 = TelescopeFactory.create_telescope('L1')
lapalma = TelescopeFactory.create_telescope('LAPALMA')
large_binocular_telescope = TelescopeFactory.create_telescope(
    'LARGE_BINOCULAR_TELESCOPE')
lasilla = TelescopeFactory.create_telescope('LASILLA')
las_campanas_observatory = TelescopeFactory.create_telescope(
    'LAS_CAMPANAS_OBSERVATORY')
la_silla_observatory = TelescopeFactory.create_telescope(
    'LA_SILLA_OBSERVATORY')
la_silla_observatory_eso = TelescopeFactory.create_telescope(
    'LA_SILLA_OBSERVATORY_(ESO)')
lbt = TelescopeFactory.create_telescope('LBT')
lco = TelescopeFactory.create_telescope('LCO')
ldt = TelescopeFactory.create_telescope('LDT')
lho = TelescopeFactory.create_telescope('LHO')
lho_4k = TelescopeFactory.create_telescope('LHO_4K')
lick = TelescopeFactory.create_telescope('LICK')
lick_observatory = TelescopeFactory.create_telescope('LICK_OBSERVATORY')
ligo_hanford_observatory = TelescopeFactory.create_telescope(
    'LIGO_HANFORD_OBSERVATORY')
ligo_livingston_observatory = TelescopeFactory.create_telescope(
    'LIGO_LIVINGSTON_OBSERVATORY')
llo = TelescopeFactory.create_telescope('LLO')
llo_4k = TelescopeFactory.create_telescope('LLO_4K')
lofar = TelescopeFactory.create_telescope('LOFAR')
long_wavelength_array_1 = TelescopeFactory.create_telescope(
    'LONG_WAVELENGTH_ARRAY_1')
lowell = TelescopeFactory.create_telescope('LOWELL')
lowell_discovery_telescope = TelescopeFactory.create_telescope(
    'LOWELL_DISCOVERY_TELESCOPE')
lowell_observatory = TelescopeFactory.create_telescope('LOWELL_OBSERVATORY')
lowell_observatory___anderson_mesa = TelescopeFactory.create_telescope(
    'LOWELL_OBSERVATORY___ANDERSON_MESA')
lowell_observatory___mars_hill = TelescopeFactory.create_telescope(
    'LOWELL_OBSERVATORY___MARS_HILL')
low_frequency_array = TelescopeFactory.create_telescope('LOW_FREQUENCY_ARRAY')
lo_am = TelescopeFactory.create_telescope('LO_AM')
lo_mh = TelescopeFactory.create_telescope('LO_MH')
lsst = TelescopeFactory.create_telescope('LSST')
lsst_1_4m = TelescopeFactory.create_telescope('LSST_1.4M')
lsst_8_4m = TelescopeFactory.create_telescope('LSST_8.4M')
lsst_auxtel = TelescopeFactory.create_telescope('LSST_AUXTEL')
lwa1 = TelescopeFactory.create_telescope('LWA1')
manastash_ridge_observatory = TelescopeFactory.create_telescope(
    'MANASTASH_RIDGE_OBSERVATORY')
mars_hill = TelescopeFactory.create_telescope('MARS_HILL')
mcdonald = TelescopeFactory.create_telescope('MCDONALD')
mcdonald_observatory = TelescopeFactory.create_telescope(
    'MCDONALD_OBSERVATORY')
mdm = TelescopeFactory.create_telescope('MDM')
mdm_observatory = TelescopeFactory.create_telescope('MDM_OBSERVATORY')
medicina = TelescopeFactory.create_telescope('MEDICINA')
medicina_dish = TelescopeFactory.create_telescope('MEDICINA_DISH')
medicina_radio_telescope = TelescopeFactory.create_telescope(
    'MEDICINA_RADIO_TELESCOPE')
meerkat = TelescopeFactory.create_telescope('MEERKAT')
mh = TelescopeFactory.create_telescope('MH')
michigan_dartmouth_mit_observatory = TelescopeFactory.create_telescope(
    'MICHIGAN_DARTMOUTH_MIT_OBSERVATORY')
mjo = TelescopeFactory.create_telescope('MJO')
mma = TelescopeFactory.create_telescope('MMA')
mmt = TelescopeFactory.create_telescope('MMT')
moa = TelescopeFactory.create_telescope('MOA')
mont_mégantic_observatory = TelescopeFactory.create_telescope(
    'MONT_MÉGANTIC_OBSERVATORY')
mount_graham_international_observatory = TelescopeFactory.create_telescope(
    'MOUNT_GRAHAM_INTERNATIONAL_OBSERVATORY')
mount_wilson_observatory = TelescopeFactory.create_telescope(
    'MOUNT_WILSON_OBSERVATORY')
mro = TelescopeFactory.create_telescope('MRO')
mso = TelescopeFactory.create_telescope('MSO')
mt__ekar_182_cm_telescope = TelescopeFactory.create_telescope(
    'MT._EKAR_182_CM_TELESCOPE')
mt__stromlo_observatory = TelescopeFactory.create_telescope(
    'MT._STROMLO_OBSERVATORY')
mtbigelow = TelescopeFactory.create_telescope('MTBIGELOW')
mt_graham = TelescopeFactory.create_telescope('MT_GRAHAM')
mt_john = TelescopeFactory.create_telescope('MT_JOHN')
multiple_mirror_telescope = TelescopeFactory.create_telescope(
    'MULTIPLE_MIRROR_TELESCOPE')
murchison_widefield_array = TelescopeFactory.create_telescope(
    'MURCHISON_WIDEFIELD_ARRAY')
murriyang = TelescopeFactory.create_telescope('MURRIYANG')
mwa = TelescopeFactory.create_telescope('MWA')
mwo = TelescopeFactory.create_telescope('MWO')
nancay = TelescopeFactory.create_telescope('NANCAY')
nancay_radio_telescope = TelescopeFactory.create_telescope(
    'NANCAY_RADIO_TELESCOPE')
nasa_infrared_telescope_facility = TelescopeFactory.create_telescope(
    'NASA_INFRARED_TELESCOPE_FACILITY')
national_observatory_of_venezuela = TelescopeFactory.create_telescope(
    'NATIONAL_OBSERVATORY_OF_VENEZUELA')
navy_precision_optical_interferometer = TelescopeFactory.create_telescope(
    'NAVY_PRECISION_OPTICAL_INTERFEROMETER')
noto = TelescopeFactory.create_telescope('NOTO')
noto_radio_telescope = TelescopeFactory.create_telescope(
    'NOTO_RADIO_TELESCOPE')
nov = TelescopeFactory.create_telescope('NOV')
nova = TelescopeFactory.create_telescope('NOVA')
npoi = TelescopeFactory.create_telescope('NPOI')
nst = TelescopeFactory.create_telescope('NST')
numi_off_axis_νe_appearance = TelescopeFactory.create_telescope(
    'NUMI_OFF_AXIS_ΝE_APPEARANCE')
oaj = TelescopeFactory.create_telescope('OAJ')
oao = TelescopeFactory.create_telescope('OAO')
oarma = TelescopeFactory.create_telescope('OARMA')
observatoire_de_haute_provence = TelescopeFactory.create_telescope(
    'OBSERVATOIRE_DE_HAUTE_PROVENCE')
observatoire_du_mont_mégantic = TelescopeFactory.create_telescope(
    'OBSERVATOIRE_DU_MONT_MÉGANTIC')
observatoire_sirene = TelescopeFactory.create_telescope('OBSERVATOIRE_SIRENE')
observatorio_astrofisico_de_javalambre = TelescopeFactory.create_telescope(
    'OBSERVATORIO_ASTROFISICO_DE_JAVALAMBRE')
observatorio_astronomico_nacional, _san_pedro_martir = TelescopeFactory.create_telescope(
    'OBSERVATORIO_ASTRONOMICO_NACIONAL,_SAN_PEDRO_MARTIR')
observatorio_astronomico_nacional, _tonantzintla = TelescopeFactory.create_telescope(
    'OBSERVATORIO_ASTRONOMICO_NACIONAL,_TONANTZINTLA')
observatorio_astronomico_ramon_maria_aller, _santiago_de_compostela = TelescopeFactory.create_telescope(
    'OBSERVATORIO_ASTRONOMICO_RAMON_MARIA_ALLER,_SANTIAGO_DE_COMPOSTELA')
observatorio_cerro_armazones = TelescopeFactory.create_telescope(
    'OBSERVATORIO_CERRO_ARMAZONES')
observatorio_del_teide = TelescopeFactory.create_telescope(
    'OBSERVATORIO_DEL_TEIDE')
observatorio_del_teide, _tenerife = TelescopeFactory.create_telescope(
    'OBSERVATORIO_DEL_TEIDE,_TENERIFE')
observatorio_de_calar_alto = TelescopeFactory.create_telescope(
    'OBSERVATORIO_DE_CALAR_ALTO')
observatorio_ramon_maria_aller = TelescopeFactory.create_telescope(
    'OBSERVATORIO_RAMON_MARIA_ALLER')
oca = TelescopeFactory.create_telescope('OCA')
ohp = TelescopeFactory.create_telescope('OHP')
okayama_astrophysical_observatory = TelescopeFactory.create_telescope(
    'OKAYAMA_ASTROPHYSICAL_OBSERVATORY')
omm = TelescopeFactory.create_telescope('OMM')
orca = TelescopeFactory.create_telescope('ORCA')
oscillation_research_with_cosmics_in_the_abyss = TelescopeFactory.create_telescope(
    'OSCILLATION_RESEARCH_WITH_COSMICS_IN_THE_ABYSS')
ot = TelescopeFactory.create_telescope('OT')
otehiwai = TelescopeFactory.create_telescope('OTEHIWAI')
otehiwai_observatory = TelescopeFactory.create_telescope(
    'OTEHIWAI_OBSERVATORY')
ovro = TelescopeFactory.create_telescope('OVRO')
owens_valley_radio_observatory = TelescopeFactory.create_telescope(
    'OWENS_VALLEY_RADIO_OBSERVATORY')
palomar = TelescopeFactory.create_telescope('PALOMAR')
paranal = TelescopeFactory.create_telescope('PARANAL')
paranal_observatory = TelescopeFactory.create_telescope('PARANAL_OBSERVATORY')
paranal_observatory_eso = TelescopeFactory.create_telescope(
    'PARANAL_OBSERVATORY_(ESO)')
parkes = TelescopeFactory.create_telescope('PARKES')
perkins = TelescopeFactory.create_telescope('PERKINS')
pto = TelescopeFactory.create_telescope('PTO')
roque_de_los_muchachos = TelescopeFactory.create_telescope(
    'ROQUE_DE_LOS_MUCHACHOS')
roque_de_los_muchachos, _la_palma = TelescopeFactory.create_telescope(
    'ROQUE_DE_LOS_MUCHACHOS,_LA_PALMA')
royal_observatory_greenwich = TelescopeFactory.create_telescope(
    'ROYAL_OBSERVATORY_GREENWICH')
rubin = TelescopeFactory.create_telescope('RUBIN')
rubin_aux = TelescopeFactory.create_telescope('RUBIN_AUX')
rubin_auxtel = TelescopeFactory.create_telescope('RUBIN_AUXTEL')
rubin_observatory = TelescopeFactory.create_telescope('RUBIN_OBSERVATORY')
saao = TelescopeFactory.create_telescope('SAAO')
sacramento_peak = TelescopeFactory.create_telescope('SACRAMENTO_PEAK')
sacramento_peak_observatory = TelescopeFactory.create_telescope(
    'SACRAMENTO_PEAK_OBSERVATORY')
sac_peak = TelescopeFactory.create_telescope('SAC_PEAK')
salt = TelescopeFactory.create_telescope('SALT')
sardinia_radio_telescope = TelescopeFactory.create_telescope(
    'SARDINIA_RADIO_TELESCOPE')
siding_spring_observatory = TelescopeFactory.create_telescope(
    'SIDING_SPRING_OBSERVATORY')
sirene = TelescopeFactory.create_telescope('SIRENE')
sno + = TelescopeFactory.create_telescope('SNO+')
southern_african_large_telescope = TelescopeFactory.create_telescope(
    'SOUTHERN_AFRICAN_LARGE_TELESCOPE')
spm = TelescopeFactory.create_telescope('SPM')
spo = TelescopeFactory.create_telescope('SPO')
srt = TelescopeFactory.create_telescope('SRT')
sso = TelescopeFactory.create_telescope('SSO')
subaru = TelescopeFactory.create_telescope('SUBARU')
subaru_telescope = TelescopeFactory.create_telescope('SUBARU_TELESCOPE')
sudbury_neutrino_observatory_ + = TelescopeFactory.create_telescope('SUDBURY_NEUTRINO_OBSERVATORY_+')
sunspot = TelescopeFactory.create_telescope('SUNSPOT')
superk = TelescopeFactory.create_telescope('SUPERK')
super_kamiokande = TelescopeFactory.create_telescope('SUPER_KAMIOKANDE')
sutherland = TelescopeFactory.create_telescope('SUTHERLAND')
teide = TelescopeFactory.create_telescope('TEIDE')
thai_national_observatory = TelescopeFactory.create_telescope(
    'THAI_NATIONAL_OBSERVATORY')
the_hale_telescope = TelescopeFactory.create_telescope('THE_HALE_TELESCOPE')
tno = TelescopeFactory.create_telescope('TNO')
tona = TelescopeFactory.create_telescope('TONA')
tubitak_national_observatory = TelescopeFactory.create_telescope(
    'TUBITAK_NATIONAL_OBSERVATORY')
tug = TelescopeFactory.create_telescope('TUG')
ukirt = TelescopeFactory.create_telescope('UKIRT')
united_kingdom_infrared_telescope = TelescopeFactory.create_telescope(
    'UNITED_KINGDOM_INFRARED_TELESCOPE')
v1 = TelescopeFactory.create_telescope('V1')
vainu_bappu_observatory = TelescopeFactory.create_telescope(
    'VAINU_BAPPU_OBSERVATORY')
vbo = TelescopeFactory.create_telescope('VBO')
very_large_array = TelescopeFactory.create_telescope('VERY_LARGE_ARRAY')
virgo = TelescopeFactory.create_telescope('VIRGO')
virgo_observatory = TelescopeFactory.create_telescope('VIRGO_OBSERVATORY')
vla = TelescopeFactory.create_telescope('VLA')
w__m__keck_observatory = TelescopeFactory.create_telescope(
    'W._M._KECK_OBSERVATORY')
whipple = TelescopeFactory.create_telescope('WHIPPLE')
whipple_observatory = TelescopeFactory.create_telescope('WHIPPLE_OBSERVATORY')
wise = TelescopeFactory.create_telescope('WISE')
wise_observatory = TelescopeFactory.create_telescope('WISE_OBSERVATORY')
wiyn = TelescopeFactory.create_telescope('WIYN')
wiyn_3_5_m = TelescopeFactory.create_telescope('WIYN_3.5_M')
wiyn_observatory = TelescopeFactory.create_telescope('WIYN_OBSERVATORY')


def print_all_telescopes(instruments: str = 'all') -> None:
    if instruments != 'all':
        raise NotImplementedError

    telescopes_list = [(telescope_name, telescope) for telescope_name,
                       telescope in globals().items() if isinstance(telescope, Telescope)]
    telescopes_list.sort(
        reverse=True, key=lambda telescopes_list: telescopes_list[1].diameter.to(u.m).value)

    logger.print('Printing available telescopes:')
    logger.info('Use the first name to access the telescope object.')
    logger.info(
        '    e.g., to access the VLT telescope, use "VLT" instead of "Very Large Telescope (VLT)"')
    logger.print('='*25)
    for (telescope_name, telescope) in telescopes_list:
        logger.print(
            f"{telescope_name} : {telescope.name} | {telescope.diameter} | Operational: {bool(telescope.operational)}")
        logger.print(
            f"    {[instrument.name for instrument in telescope.instruments]}")


if __name__ == '__main__':
    logger.warning('='*25)
    logger.warning('Debugging mode: Telescopes module')
    logger.warning('='*25)
    print_all_telescopes()
    from . import instruments as inst
    inst.print_all_spectrographs()

    print([mode for mode in inst.ESPRESSO.modes if mode.exposure_time_calculator is not None])

    for mode in [mode for mode in inst.ESPRESSO.modes if mode.exposure_time_calculator is not None]:
        mode.exposure_time_calculator.open_all_scenarios(
            stellar_temperature=5500)

    logger.warning('='*25)
    logger.warning('End of debugging mode: Telescopes module')
    logger.warning('='*25)
