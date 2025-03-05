
import dataclasses

@dataclasses.dataclass
class RoleType(object):
    id: str
    name: str
    rights: list[str]
    requires_2fa: bool
    group_type: "GroupType"
    
    def __hash__(self):
        return hash(id)
    
    def __eq__(self, other):
        return isinstance(other, RoleType) and self.id == other.id
    

@dataclasses.dataclass
class GroupType(object):
    id: str
    name: str
    role_types: list[RoleType]
    
    def __hash__(self):
        return hash(id)
        
    def __eq__(self, other):
        return isinstance(other, GroupType) and self.id == other.id
    
GROUP_ROOT = GroupType("Group::Root", "Organisation", [])
GROUP_FEDERATION = GroupType("Group::Federation", "Bund", [])
GROUP_FEDERALBOARD = GroupType("Group::FederalBoard", "Bund - Bundesleitung", [])
GROUP_ORGANIZATIONBOARD = GroupType("Group::OrganizationBoard", "Bund - Verbandsleitung", [])
GROUP_FEDERALPROFESSIONALGROUP = GroupType("Group::FederalProfessionalGroup", "Bund - Fachgruppe", [])
GROUP_FEDERALWORKGROUP = GroupType("Group::FederalWorkGroup", "Bund - Arbeitsgruppe", [])
GROUP_FEDERALALUMNUSGROUP = GroupType("Group::FederalAlumnusGroup", "Bund - Ehemalige", [])
GROUP_STATE = GroupType("Group::State", "Kanton", [])
GROUP_STATEAGENCY = GroupType("Group::StateAgency", "Kanton - Arbeitsstelle", [])
GROUP_STATEBOARD = GroupType("Group::StateBoard", "Kanton - Kantonsleitung", [])
GROUP_STATEPROFESSIONALGROUP = GroupType("Group::StateProfessionalGroup", "Kanton - Fachgruppe", [])
GROUP_STATEWORKGROUP = GroupType("Group::StateWorkGroup", "Kanton - Arbeitsgruppe", [])
GROUP_STATEALUMNUSGROUP = GroupType("Group::StateAlumnusGroup", "Kanton - Ehemalige", [])
GROUP_REGION = GroupType("Group::Region", "Region", [])
GROUP_REGIONALBOARD = GroupType("Group::RegionalBoard", "Region - Regionalleitung", [])
GROUP_REGIONALPROFESSIONALGROUP = GroupType("Group::RegionalProfessionalGroup", "Region - Fachgruppe", [])
GROUP_REGIONALWORKGROUP = GroupType("Group::RegionalWorkGroup", "Region - Arbeitsgruppe", [])
GROUP_REGIONALALUMNUSGROUP = GroupType("Group::RegionalAlumnusGroup", "Region - Ehemalige", [])
GROUP_FLOCK = GroupType("Group::Flock", "Schar", [])
GROUP_CHILDGROUP = GroupType("Group::ChildGroup", "Schar - Kindergruppe", [])
GROUP_FLOCKALUMNUSGROUP = GroupType("Group::FlockAlumnusGroup", "Schar - Ehemalige", [])
GROUP_NEJB = GroupType("Group::Nejb", "NEJB", [])
GROUP_NEJBBUNDESLEITUNG = GroupType("Group::NejbBundesleitung", "NEJB - NEJB Bundesleitung", [])
GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING = GroupType("Group::NetzwerkEhemaligeJungwachtBlauring", "NEJB - Netzwerk Ehemalige Jungwacht Blauring", [])
GROUP_NEJBKANTON = GroupType("Group::NejbKanton", "Kanton (Ehemalige)", [])
GROUP_KANTONEHEMALIGENVEREIN = GroupType("Group::KantonEhemaligenverein", "Kanton (Ehemalige) - Kantonaler Ehemaligenverein", [])
GROUP_NEJBREGION = GroupType("Group::NejbRegion", "Region (Ehemalige)", [])
GROUP_REGIONEHEMALIGENVEREIN = GroupType("Group::RegionEhemaligenverein", "Region (Ehemalige) - Regionaler Ehemaligenverein", [])
GROUP_NEJBSCHAR = GroupType("Group::NejbSchar", "Ehemaligenverein (Schar)", [])
GROUP_SIMPLEGROUP = GroupType("Group::SimpleGroup", "Global - Einfache Gruppe", [])
GROUP_NEJBSIMPLEGROUP = GroupType("Group::NejbSimpleGroup", "Global - Einfache Gruppe (Ehemalige)", [])

ROLE_ROOT_ADMIN = RoleType("Group::Root::Admin", "Administrator", [":layer_and_below_full", ":admin"], True, GROUP_ROOT)
ROLE_FEDERATION_GROUPADMIN = RoleType("Group::Federation::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_FEDERATION)
ROLE_FEDERATION_ALUMNUS = RoleType("Group::Federation::Alumnus", "Austritt", [":group_read"], False, GROUP_FEDERATION)
ROLE_FEDERATION_EXTERNAL = RoleType("Group::Federation::External", "Extern", [], False, GROUP_FEDERATION)
ROLE_FEDERATION_DISPATCHADDRESS = RoleType("Group::Federation::DispatchAddress", "Versandadresse", [], False, GROUP_FEDERATION)
ROLE_FEDERATION_ITSUPPORT = RoleType("Group::Federation::ItSupport", "IT Support", [":impersonation"], False, GROUP_FEDERATION)
ROLE_FEDERALBOARD_MEMBER = RoleType("Group::FederalBoard::Member", "Mitglied", [":admin", ":layer_and_below_full", ":contact_data"], False, GROUP_FEDERALBOARD)
ROLE_FEDERALBOARD_PRESIDENT = RoleType("Group::FederalBoard::President", "Präses", [":admin", ":layer_and_below_full", ":contact_data"], False, GROUP_FEDERALBOARD)
ROLE_FEDERALBOARD_GROUPADMIN = RoleType("Group::FederalBoard::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_FEDERALBOARD)
ROLE_FEDERALBOARD_ALUMNUS = RoleType("Group::FederalBoard::Alumnus", "Austritt", [":group_read"], False, GROUP_FEDERALBOARD)
ROLE_FEDERALBOARD_EXTERNAL = RoleType("Group::FederalBoard::External", "Extern", [], False, GROUP_FEDERALBOARD)
ROLE_FEDERALBOARD_DISPATCHADDRESS = RoleType("Group::FederalBoard::DispatchAddress", "Versandadresse", [], False, GROUP_FEDERALBOARD)
ROLE_FEDERALBOARD_TREASURER = RoleType("Group::FederalBoard::Treasurer", "Kassier*in", [":layer_and_below_read", ":finance", ":contact_data"], True, GROUP_FEDERALBOARD)
ROLE_ORGANIZATIONBOARD_LEADER = RoleType("Group::OrganizationBoard::Leader", "Leitung", [":group_full", ":contact_data"], False, GROUP_ORGANIZATIONBOARD)
ROLE_ORGANIZATIONBOARD_TREASURER = RoleType("Group::OrganizationBoard::Treasurer", "Kassier*in", [":contact_data", ":group_read", ":finance"], True, GROUP_ORGANIZATIONBOARD)
ROLE_ORGANIZATIONBOARD_MEMBER = RoleType("Group::OrganizationBoard::Member", "Mitglied", [":contact_data", ":group_read"], False, GROUP_ORGANIZATIONBOARD)
ROLE_ORGANIZATIONBOARD_GROUPADMIN = RoleType("Group::OrganizationBoard::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_ORGANIZATIONBOARD)
ROLE_ORGANIZATIONBOARD_ALUMNUS = RoleType("Group::OrganizationBoard::Alumnus", "Austritt", [":group_read"], False, GROUP_ORGANIZATIONBOARD)
ROLE_ORGANIZATIONBOARD_EXTERNAL = RoleType("Group::OrganizationBoard::External", "Extern", [], False, GROUP_ORGANIZATIONBOARD)
ROLE_ORGANIZATIONBOARD_DISPATCHADDRESS = RoleType("Group::OrganizationBoard::DispatchAddress", "Versandadresse", [], False, GROUP_ORGANIZATIONBOARD)
ROLE_FEDERALPROFESSIONALGROUP_LEADER = RoleType("Group::FederalProfessionalGroup::Leader", "Leitung", [":group_full", ":contact_data"], False, GROUP_FEDERALPROFESSIONALGROUP)
ROLE_FEDERALPROFESSIONALGROUP_MEMBER = RoleType("Group::FederalProfessionalGroup::Member", "Mitglied", [":group_read", ":contact_data"], False, GROUP_FEDERALPROFESSIONALGROUP)
ROLE_FEDERALPROFESSIONALGROUP_GROUPADMIN = RoleType("Group::FederalProfessionalGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_FEDERALPROFESSIONALGROUP)
ROLE_FEDERALPROFESSIONALGROUP_ALUMNUS = RoleType("Group::FederalProfessionalGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_FEDERALPROFESSIONALGROUP)
ROLE_FEDERALPROFESSIONALGROUP_EXTERNAL = RoleType("Group::FederalProfessionalGroup::External", "Extern", [], False, GROUP_FEDERALPROFESSIONALGROUP)
ROLE_FEDERALPROFESSIONALGROUP_DISPATCHADDRESS = RoleType("Group::FederalProfessionalGroup::DispatchAddress", "Versandadresse", [], False, GROUP_FEDERALPROFESSIONALGROUP)
ROLE_FEDERALPROFESSIONALGROUP_TREASURER = RoleType("Group::FederalProfessionalGroup::Treasurer", "Kassier*in", [":layer_and_below_read", ":finance", ":contact_data"], True, GROUP_FEDERALPROFESSIONALGROUP)
ROLE_FEDERALWORKGROUP_LEADER = RoleType("Group::FederalWorkGroup::Leader", "Leitung", [":group_full", ":contact_data"], False, GROUP_FEDERALWORKGROUP)
ROLE_FEDERALWORKGROUP_MEMBER = RoleType("Group::FederalWorkGroup::Member", "Mitglied", [":group_read"], False, GROUP_FEDERALWORKGROUP)
ROLE_FEDERALWORKGROUP_GROUPADMIN = RoleType("Group::FederalWorkGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_FEDERALWORKGROUP)
ROLE_FEDERALWORKGROUP_ALUMNUS = RoleType("Group::FederalWorkGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_FEDERALWORKGROUP)
ROLE_FEDERALWORKGROUP_EXTERNAL = RoleType("Group::FederalWorkGroup::External", "Extern", [], False, GROUP_FEDERALWORKGROUP)
ROLE_FEDERALWORKGROUP_DISPATCHADDRESS = RoleType("Group::FederalWorkGroup::DispatchAddress", "Versandadresse", [], False, GROUP_FEDERALWORKGROUP)
ROLE_FEDERALWORKGROUP_TREASURER = RoleType("Group::FederalWorkGroup::Treasurer", "Kassier*in", [":layer_and_below_read", ":finance", ":contact_data"], True, GROUP_FEDERALWORKGROUP)
ROLE_FEDERALALUMNUSGROUP_LEADER = RoleType("Group::FederalAlumnusGroup::Leader", "Leitung", [":group_and_below_full", ":contact_data", ":alumnus_below_full"], False, GROUP_FEDERALALUMNUSGROUP)
ROLE_FEDERALALUMNUSGROUP_GROUPADMIN = RoleType("Group::FederalAlumnusGroup::GroupAdmin", "Adressverwaltung", [":group_and_below_full"], False, GROUP_FEDERALALUMNUSGROUP)
ROLE_FEDERALALUMNUSGROUP_TREASURER = RoleType("Group::FederalAlumnusGroup::Treasurer", "Kassier*in", [":group_and_below_read"], False, GROUP_FEDERALALUMNUSGROUP)
ROLE_FEDERALALUMNUSGROUP_MEMBER = RoleType("Group::FederalAlumnusGroup::Member", "Mitglied", [":group_read"], False, GROUP_FEDERALALUMNUSGROUP)
ROLE_FEDERALALUMNUSGROUP_EXTERNAL = RoleType("Group::FederalAlumnusGroup::External", "Extern", [], False, GROUP_FEDERALALUMNUSGROUP)
ROLE_FEDERALALUMNUSGROUP_DISPATCHADDRESS = RoleType("Group::FederalAlumnusGroup::DispatchAddress", "Versandadresse", [], False, GROUP_FEDERALALUMNUSGROUP)
ROLE_STATE_COACH = RoleType("Group::State::Coach", "Coach", [":contact_data", ":group_read"], False, GROUP_STATE)
ROLE_STATE_GROUPADMIN = RoleType("Group::State::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_STATE)
ROLE_STATE_ALUMNUS = RoleType("Group::State::Alumnus", "Austritt", [":group_read"], False, GROUP_STATE)
ROLE_STATE_EXTERNAL = RoleType("Group::State::External", "Extern", [], False, GROUP_STATE)
ROLE_STATE_DISPATCHADDRESS = RoleType("Group::State::DispatchAddress", "Versandadresse", [], False, GROUP_STATE)
ROLE_STATEAGENCY_LEADER = RoleType("Group::StateAgency::Leader", "Leitung", [":layer_and_below_full", ":contact_data"], False, GROUP_STATEAGENCY)
ROLE_STATEAGENCY_GROUPADMIN = RoleType("Group::StateAgency::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_STATEAGENCY)
ROLE_STATEAGENCY_ALUMNUS = RoleType("Group::StateAgency::Alumnus", "Austritt", [":group_read"], False, GROUP_STATEAGENCY)
ROLE_STATEAGENCY_EXTERNAL = RoleType("Group::StateAgency::External", "Extern", [], False, GROUP_STATEAGENCY)
ROLE_STATEAGENCY_DISPATCHADDRESS = RoleType("Group::StateAgency::DispatchAddress", "Versandadresse", [], False, GROUP_STATEAGENCY)
ROLE_STATEBOARD_LEADER = RoleType("Group::StateBoard::Leader", "Leitung", [":group_full", ":layer_and_below_read", ":contact_data"], False, GROUP_STATEBOARD)
ROLE_STATEBOARD_MEMBER = RoleType("Group::StateBoard::Member", "Mitglied", [":group_read", ":contact_data"], False, GROUP_STATEBOARD)
ROLE_STATEBOARD_SUPERVISOR = RoleType("Group::StateBoard::Supervisor", "Stellenbegleitung", [":layer_and_below_read"], False, GROUP_STATEBOARD)
ROLE_STATEBOARD_PRESIDENT = RoleType("Group::StateBoard::President", "Präses", [":group_read", ":contact_data"], False, GROUP_STATEBOARD)
ROLE_STATEBOARD_GROUPADMIN = RoleType("Group::StateBoard::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_STATEBOARD)
ROLE_STATEBOARD_ALUMNUS = RoleType("Group::StateBoard::Alumnus", "Austritt", [":group_read"], False, GROUP_STATEBOARD)
ROLE_STATEBOARD_EXTERNAL = RoleType("Group::StateBoard::External", "Extern", [], False, GROUP_STATEBOARD)
ROLE_STATEBOARD_DISPATCHADDRESS = RoleType("Group::StateBoard::DispatchAddress", "Versandadresse", [], False, GROUP_STATEBOARD)
ROLE_STATEPROFESSIONALGROUP_LEADER = RoleType("Group::StateProfessionalGroup::Leader", "Leitung", [":group_full", ":contact_data"], False, GROUP_STATEPROFESSIONALGROUP)
ROLE_STATEPROFESSIONALGROUP_MEMBER = RoleType("Group::StateProfessionalGroup::Member", "Mitglied", [":group_read"], False, GROUP_STATEPROFESSIONALGROUP)
ROLE_STATEPROFESSIONALGROUP_GROUPADMIN = RoleType("Group::StateProfessionalGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_STATEPROFESSIONALGROUP)
ROLE_STATEPROFESSIONALGROUP_ALUMNUS = RoleType("Group::StateProfessionalGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_STATEPROFESSIONALGROUP)
ROLE_STATEPROFESSIONALGROUP_EXTERNAL = RoleType("Group::StateProfessionalGroup::External", "Extern", [], False, GROUP_STATEPROFESSIONALGROUP)
ROLE_STATEPROFESSIONALGROUP_DISPATCHADDRESS = RoleType("Group::StateProfessionalGroup::DispatchAddress", "Versandadresse", [], False, GROUP_STATEPROFESSIONALGROUP)
ROLE_STATEWORKGROUP_LEADER = RoleType("Group::StateWorkGroup::Leader", "Leitung", [":group_full", ":contact_data"], False, GROUP_STATEWORKGROUP)
ROLE_STATEWORKGROUP_MEMBER = RoleType("Group::StateWorkGroup::Member", "Mitglied", [":group_read"], False, GROUP_STATEWORKGROUP)
ROLE_STATEWORKGROUP_GROUPADMIN = RoleType("Group::StateWorkGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_STATEWORKGROUP)
ROLE_STATEWORKGROUP_ALUMNUS = RoleType("Group::StateWorkGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_STATEWORKGROUP)
ROLE_STATEWORKGROUP_EXTERNAL = RoleType("Group::StateWorkGroup::External", "Extern", [], False, GROUP_STATEWORKGROUP)
ROLE_STATEWORKGROUP_DISPATCHADDRESS = RoleType("Group::StateWorkGroup::DispatchAddress", "Versandadresse", [], False, GROUP_STATEWORKGROUP)
ROLE_STATEALUMNUSGROUP_LEADER = RoleType("Group::StateAlumnusGroup::Leader", "Leitung", [":group_and_below_full", ":contact_data", ":alumnus_below_full"], False, GROUP_STATEALUMNUSGROUP)
ROLE_STATEALUMNUSGROUP_GROUPADMIN = RoleType("Group::StateAlumnusGroup::GroupAdmin", "Adressverwaltung", [":group_and_below_full"], False, GROUP_STATEALUMNUSGROUP)
ROLE_STATEALUMNUSGROUP_TREASURER = RoleType("Group::StateAlumnusGroup::Treasurer", "Kassier*in", [":group_and_below_read"], False, GROUP_STATEALUMNUSGROUP)
ROLE_STATEALUMNUSGROUP_MEMBER = RoleType("Group::StateAlumnusGroup::Member", "Mitglied", [":group_read"], False, GROUP_STATEALUMNUSGROUP)
ROLE_STATEALUMNUSGROUP_EXTERNAL = RoleType("Group::StateAlumnusGroup::External", "Extern", [], False, GROUP_STATEALUMNUSGROUP)
ROLE_STATEALUMNUSGROUP_DISPATCHADDRESS = RoleType("Group::StateAlumnusGroup::DispatchAddress", "Versandadresse", [], False, GROUP_STATEALUMNUSGROUP)
ROLE_REGION_COACH = RoleType("Group::Region::Coach", "Coach", [":contact_data", ":group_read"], False, GROUP_REGION)
ROLE_REGION_GROUPADMIN = RoleType("Group::Region::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_REGION)
ROLE_REGION_ALUMNUS = RoleType("Group::Region::Alumnus", "Austritt", [":group_read"], False, GROUP_REGION)
ROLE_REGION_EXTERNAL = RoleType("Group::Region::External", "Extern", [], False, GROUP_REGION)
ROLE_REGION_DISPATCHADDRESS = RoleType("Group::Region::DispatchAddress", "Versandadresse", [], False, GROUP_REGION)
ROLE_REGIONALBOARD_LEADER = RoleType("Group::RegionalBoard::Leader", "Leitung", [":layer_and_below_full", ":contact_data"], False, GROUP_REGIONALBOARD)
ROLE_REGIONALBOARD_MEMBER = RoleType("Group::RegionalBoard::Member", "Mitglied", [":layer_and_below_read", ":contact_data"], False, GROUP_REGIONALBOARD)
ROLE_REGIONALBOARD_PRESIDENT = RoleType("Group::RegionalBoard::President", "Präses", [":layer_and_below_read", ":contact_data"], False, GROUP_REGIONALBOARD)
ROLE_REGIONALBOARD_GROUPADMIN = RoleType("Group::RegionalBoard::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_REGIONALBOARD)
ROLE_REGIONALBOARD_ALUMNUS = RoleType("Group::RegionalBoard::Alumnus", "Austritt", [":group_read"], False, GROUP_REGIONALBOARD)
ROLE_REGIONALBOARD_EXTERNAL = RoleType("Group::RegionalBoard::External", "Extern", [], False, GROUP_REGIONALBOARD)
ROLE_REGIONALBOARD_DISPATCHADDRESS = RoleType("Group::RegionalBoard::DispatchAddress", "Versandadresse", [], False, GROUP_REGIONALBOARD)
ROLE_REGIONALPROFESSIONALGROUP_LEADER = RoleType("Group::RegionalProfessionalGroup::Leader", "Leitung", [":group_full", ":contact_data"], False, GROUP_REGIONALPROFESSIONALGROUP)
ROLE_REGIONALPROFESSIONALGROUP_MEMBER = RoleType("Group::RegionalProfessionalGroup::Member", "Mitglied", [":group_read"], False, GROUP_REGIONALPROFESSIONALGROUP)
ROLE_REGIONALPROFESSIONALGROUP_GROUPADMIN = RoleType("Group::RegionalProfessionalGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_REGIONALPROFESSIONALGROUP)
ROLE_REGIONALPROFESSIONALGROUP_ALUMNUS = RoleType("Group::RegionalProfessionalGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_REGIONALPROFESSIONALGROUP)
ROLE_REGIONALPROFESSIONALGROUP_EXTERNAL = RoleType("Group::RegionalProfessionalGroup::External", "Extern", [], False, GROUP_REGIONALPROFESSIONALGROUP)
ROLE_REGIONALPROFESSIONALGROUP_DISPATCHADDRESS = RoleType("Group::RegionalProfessionalGroup::DispatchAddress", "Versandadresse", [], False, GROUP_REGIONALPROFESSIONALGROUP)
ROLE_REGIONALWORKGROUP_LEADER = RoleType("Group::RegionalWorkGroup::Leader", "Leitung", [":group_full", ":contact_data"], False, GROUP_REGIONALWORKGROUP)
ROLE_REGIONALWORKGROUP_MEMBER = RoleType("Group::RegionalWorkGroup::Member", "Mitglied", [":group_read"], False, GROUP_REGIONALWORKGROUP)
ROLE_REGIONALWORKGROUP_GROUPADMIN = RoleType("Group::RegionalWorkGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_REGIONALWORKGROUP)
ROLE_REGIONALWORKGROUP_ALUMNUS = RoleType("Group::RegionalWorkGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_REGIONALWORKGROUP)
ROLE_REGIONALWORKGROUP_EXTERNAL = RoleType("Group::RegionalWorkGroup::External", "Extern", [], False, GROUP_REGIONALWORKGROUP)
ROLE_REGIONALWORKGROUP_DISPATCHADDRESS = RoleType("Group::RegionalWorkGroup::DispatchAddress", "Versandadresse", [], False, GROUP_REGIONALWORKGROUP)
ROLE_REGIONALALUMNUSGROUP_LEADER = RoleType("Group::RegionalAlumnusGroup::Leader", "Leitung", [":group_and_below_full", ":contact_data", ":alumnus_below_full"], False, GROUP_REGIONALALUMNUSGROUP)
ROLE_REGIONALALUMNUSGROUP_GROUPADMIN = RoleType("Group::RegionalAlumnusGroup::GroupAdmin", "Adressverwaltung", [":group_and_below_full"], False, GROUP_REGIONALALUMNUSGROUP)
ROLE_REGIONALALUMNUSGROUP_TREASURER = RoleType("Group::RegionalAlumnusGroup::Treasurer", "Kassier*in", [":group_and_below_read"], False, GROUP_REGIONALALUMNUSGROUP)
ROLE_REGIONALALUMNUSGROUP_MEMBER = RoleType("Group::RegionalAlumnusGroup::Member", "Mitglied", [":group_read"], False, GROUP_REGIONALALUMNUSGROUP)
ROLE_REGIONALALUMNUSGROUP_EXTERNAL = RoleType("Group::RegionalAlumnusGroup::External", "Extern", [], False, GROUP_REGIONALALUMNUSGROUP)
ROLE_REGIONALALUMNUSGROUP_DISPATCHADDRESS = RoleType("Group::RegionalAlumnusGroup::DispatchAddress", "Versandadresse", [], False, GROUP_REGIONALALUMNUSGROUP)
ROLE_FLOCK_LEADER = RoleType("Group::Flock::Leader", "Scharleitung", [":layer_and_below_full", ":contact_data", ":approve_applications"], False, GROUP_FLOCK)
ROLE_FLOCK_CAMPLEADER = RoleType("Group::Flock::CampLeader", "Lagerleitung", [":layer_and_below_full", ":contact_data"], False, GROUP_FLOCK)
ROLE_FLOCK_PRESIDENT = RoleType("Group::Flock::President", "Präses", [":layer_and_below_read", ":contact_data"], False, GROUP_FLOCK)
ROLE_FLOCK_TREASURER = RoleType("Group::Flock::Treasurer", "Kassier*in", [":layer_and_below_read", ":contact_data"], False, GROUP_FLOCK)
ROLE_FLOCK_GUIDE = RoleType("Group::Flock::Guide", "Leiter/in", [":layer_and_below_read"], False, GROUP_FLOCK)
ROLE_FLOCK_GROUPADMIN = RoleType("Group::Flock::GroupAdmin", "Adressverwaltung", [":layer_and_below_full"], False, GROUP_FLOCK)
ROLE_FLOCK_ALUMNUS = RoleType("Group::Flock::Alumnus", "Austritt", [":group_read"], False, GROUP_FLOCK)
ROLE_FLOCK_EXTERNAL = RoleType("Group::Flock::External", "Extern", [], False, GROUP_FLOCK)
ROLE_FLOCK_DISPATCHADDRESS = RoleType("Group::Flock::DispatchAddress", "Versandadresse", [], False, GROUP_FLOCK)
ROLE_CHILDGROUP_LEADER = RoleType("Group::ChildGroup::Leader", "Leitung", [":group_full"], False, GROUP_CHILDGROUP)
ROLE_CHILDGROUP_CHILD = RoleType("Group::ChildGroup::Child", "Kind", [], False, GROUP_CHILDGROUP)
ROLE_CHILDGROUP_GROUPADMIN = RoleType("Group::ChildGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_CHILDGROUP)
ROLE_CHILDGROUP_ALUMNUS = RoleType("Group::ChildGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_CHILDGROUP)
ROLE_CHILDGROUP_EXTERNAL = RoleType("Group::ChildGroup::External", "Extern", [], False, GROUP_CHILDGROUP)
ROLE_CHILDGROUP_DISPATCHADDRESS = RoleType("Group::ChildGroup::DispatchAddress", "Versandadresse", [], False, GROUP_CHILDGROUP)
ROLE_FLOCKALUMNUSGROUP_LEADER = RoleType("Group::FlockAlumnusGroup::Leader", "Leitung", [":group_and_below_full", ":contact_data", ":alumnus_below_full"], False, GROUP_FLOCKALUMNUSGROUP)
ROLE_FLOCKALUMNUSGROUP_GROUPADMIN = RoleType("Group::FlockAlumnusGroup::GroupAdmin", "Adressverwaltung", [":group_and_below_full"], False, GROUP_FLOCKALUMNUSGROUP)
ROLE_FLOCKALUMNUSGROUP_TREASURER = RoleType("Group::FlockAlumnusGroup::Treasurer", "Kassier*in", [":group_and_below_read"], False, GROUP_FLOCKALUMNUSGROUP)
ROLE_FLOCKALUMNUSGROUP_MEMBER = RoleType("Group::FlockAlumnusGroup::Member", "Mitglied", [":group_read"], False, GROUP_FLOCKALUMNUSGROUP)
ROLE_FLOCKALUMNUSGROUP_EXTERNAL = RoleType("Group::FlockAlumnusGroup::External", "Extern", [], False, GROUP_FLOCKALUMNUSGROUP)
ROLE_FLOCKALUMNUSGROUP_DISPATCHADDRESS = RoleType("Group::FlockAlumnusGroup::DispatchAddress", "Versandadresse", [], False, GROUP_FLOCKALUMNUSGROUP)
ROLE_NEJB_GROUPADMIN = RoleType("Group::Nejb::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_NEJB)
ROLE_NEJB_DISPATCHADDRESS = RoleType("Group::Nejb::DispatchAddress", "Versandadresse", [], False, GROUP_NEJB)
ROLE_NEJB_ITSUPPORT = RoleType("Group::Nejb::ITSupport", "IT Support", [":admin", ":impersonation"], False, GROUP_NEJB)
ROLE_NEJBBUNDESLEITUNG_GROUPADMIN = RoleType("Group::NejbBundesleitung::GroupAdmin", "Adressverwaltung", [":admin", ":layer_and_below_full", ":contact_data"], False, GROUP_NEJBBUNDESLEITUNG)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_LEADER = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::Leader", "Leitung", [":group_and_below_full", ":contact_data"], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_GROUPADMIN = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::GroupAdmin", "Adressverwaltung", [":group_and_below_full"], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_TREASURER = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::Treasurer", "Kassier*in", [":group_and_below_read"], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_ACTIVEMEMBER = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::ActiveMember", "Aktivmitglied", [":group_read"], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_PASSIVEMEMBER = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::PassiveMember", "Passivmitglied", [":group_read"], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_COLLECTIVEMEMBER = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::CollectiveMember", "Kollektivmitglied", [":group_read"], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_NEJBJOINER = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::NejbJoiner", "Neumitglied", [], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_EXTERNAL = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::External", "Extern", [], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_DISPATCHADDRESS = RoleType("Group::NetzwerkEhemaligeJungwachtBlauring::DispatchAddress", "Versandadresse", [], False, GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING)
ROLE_NEJBKANTON_GROUPADMIN = RoleType("Group::NejbKanton::GroupAdmin", "Adressverwaltung", [":admin", ":layer_and_below_full", ":contact_data"], False, GROUP_NEJBKANTON)
ROLE_KANTONEHEMALIGENVEREIN_LEADER = RoleType("Group::KantonEhemaligenverein::Leader", "Leitung", [":group_and_below_full", ":contact_data"], False, GROUP_KANTONEHEMALIGENVEREIN)
ROLE_KANTONEHEMALIGENVEREIN_GROUPADMIN = RoleType("Group::KantonEhemaligenverein::GroupAdmin", "Adressverwaltung", [":group_and_below_full"], False, GROUP_KANTONEHEMALIGENVEREIN)
ROLE_KANTONEHEMALIGENVEREIN_TREASURER = RoleType("Group::KantonEhemaligenverein::Treasurer", "Kassier*in", [":group_and_below_read"], False, GROUP_KANTONEHEMALIGENVEREIN)
ROLE_KANTONEHEMALIGENVEREIN_NEJBMEMBER = RoleType("Group::KantonEhemaligenverein::NejbMember", "Mitglied Ehemalige", [":group_read"], False, GROUP_KANTONEHEMALIGENVEREIN)
ROLE_KANTONEHEMALIGENVEREIN_NEJBJOINER = RoleType("Group::KantonEhemaligenverein::NejbJoiner", "Neumitglied", [], False, GROUP_KANTONEHEMALIGENVEREIN)
ROLE_KANTONEHEMALIGENVEREIN_EXTERNAL = RoleType("Group::KantonEhemaligenverein::External", "Extern", [], False, GROUP_KANTONEHEMALIGENVEREIN)
ROLE_KANTONEHEMALIGENVEREIN_DISPATCHADDRESS = RoleType("Group::KantonEhemaligenverein::DispatchAddress", "Versandadresse", [], False, GROUP_KANTONEHEMALIGENVEREIN)
ROLE_NEJBREGION_GROUPADMIN = RoleType("Group::NejbRegion::GroupAdmin", "Adressverwaltung", [":admin", ":layer_and_below_full", ":contact_data"], False, GROUP_NEJBREGION)
ROLE_REGIONEHEMALIGENVEREIN_LEADER = RoleType("Group::RegionEhemaligenverein::Leader", "Leitung", [":group_and_below_full", ":contact_data"], False, GROUP_REGIONEHEMALIGENVEREIN)
ROLE_REGIONEHEMALIGENVEREIN_GROUPADMIN = RoleType("Group::RegionEhemaligenverein::GroupAdmin", "Adressverwaltung", [":group_and_below_full"], False, GROUP_REGIONEHEMALIGENVEREIN)
ROLE_REGIONEHEMALIGENVEREIN_TREASURER = RoleType("Group::RegionEhemaligenverein::Treasurer", "Kassier*in", [":group_and_below_read"], False, GROUP_REGIONEHEMALIGENVEREIN)
ROLE_REGIONEHEMALIGENVEREIN_NEJBMEMBER = RoleType("Group::RegionEhemaligenverein::NejbMember", "Mitglied Ehemalige", [":group_read"], False, GROUP_REGIONEHEMALIGENVEREIN)
ROLE_REGIONEHEMALIGENVEREIN_NEJBJOINER = RoleType("Group::RegionEhemaligenverein::NejbJoiner", "Neumitglied", [], False, GROUP_REGIONEHEMALIGENVEREIN)
ROLE_REGIONEHEMALIGENVEREIN_EXTERNAL = RoleType("Group::RegionEhemaligenverein::External", "Extern", [], False, GROUP_REGIONEHEMALIGENVEREIN)
ROLE_REGIONEHEMALIGENVEREIN_DISPATCHADDRESS = RoleType("Group::RegionEhemaligenverein::DispatchAddress", "Versandadresse", [], False, GROUP_REGIONEHEMALIGENVEREIN)
ROLE_NEJBSCHAR_LEADER = RoleType("Group::NejbSchar::Leader", "Leitung", [":layer_full", ":contact_data"], False, GROUP_NEJBSCHAR)
ROLE_NEJBSCHAR_GROUPADMIN = RoleType("Group::NejbSchar::GroupAdmin", "Adressverwaltung", [":layer_full"], False, GROUP_NEJBSCHAR)
ROLE_NEJBSCHAR_TREASURER = RoleType("Group::NejbSchar::Treasurer", "Kassier*in", [":layer_read"], False, GROUP_NEJBSCHAR)
ROLE_NEJBSCHAR_NEJBMEMBER = RoleType("Group::NejbSchar::NejbMember", "Mitglied Ehemalige", [":group_read"], False, GROUP_NEJBSCHAR)
ROLE_NEJBSCHAR_NEJBJOINER = RoleType("Group::NejbSchar::NejbJoiner", "Neumitglied", [], False, GROUP_NEJBSCHAR)
ROLE_NEJBSCHAR_EXTERNAL = RoleType("Group::NejbSchar::External", "Extern", [], False, GROUP_NEJBSCHAR)
ROLE_NEJBSCHAR_DISPATCHADDRESS = RoleType("Group::NejbSchar::DispatchAddress", "Versandadresse", [], False, GROUP_NEJBSCHAR)
ROLE_SIMPLEGROUP_LEADER = RoleType("Group::SimpleGroup::Leader", "Leitung", [":group_full"], False, GROUP_SIMPLEGROUP)
ROLE_SIMPLEGROUP_MEMBER = RoleType("Group::SimpleGroup::Member", "Mitglied", [":group_read"], False, GROUP_SIMPLEGROUP)
ROLE_SIMPLEGROUP_GROUPADMIN = RoleType("Group::SimpleGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_SIMPLEGROUP)
ROLE_SIMPLEGROUP_ALUMNUS = RoleType("Group::SimpleGroup::Alumnus", "Austritt", [":group_read"], False, GROUP_SIMPLEGROUP)
ROLE_SIMPLEGROUP_EXTERNAL = RoleType("Group::SimpleGroup::External", "Extern", [], False, GROUP_SIMPLEGROUP)
ROLE_SIMPLEGROUP_DISPATCHADDRESS = RoleType("Group::SimpleGroup::DispatchAddress", "Versandadresse", [], False, GROUP_SIMPLEGROUP)
ROLE_NEJBSIMPLEGROUP_LEADER = RoleType("Group::NejbSimpleGroup::Leader", "Leitung", [":group_full"], False, GROUP_NEJBSIMPLEGROUP)
ROLE_NEJBSIMPLEGROUP_MEMBER = RoleType("Group::NejbSimpleGroup::Member", "Mitglied Ehemalige", [":group_read"], False, GROUP_NEJBSIMPLEGROUP)
ROLE_NEJBSIMPLEGROUP_GROUPADMIN = RoleType("Group::NejbSimpleGroup::GroupAdmin", "Adressverwaltung", [":group_full"], False, GROUP_NEJBSIMPLEGROUP)
ROLE_NEJBSIMPLEGROUP_EXTERNAL = RoleType("Group::NejbSimpleGroup::External", "Extern", [], False, GROUP_NEJBSIMPLEGROUP)
ROLE_NEJBSIMPLEGROUP_DISPATCHADDRESS = RoleType("Group::NejbSimpleGroup::DispatchAddress", "Versandadresse", [], False, GROUP_NEJBSIMPLEGROUP)
ROLE_NEJBSIMPLEGROUP_NEWJOINER = RoleType("Group::NejbSimpleGroup::NewJoiner", "Neumitglied", [], False, GROUP_NEJBSIMPLEGROUP)

GROUP_ROOT.role_types = [ROLE_ROOT_ADMIN]
GROUP_FEDERATION.role_types = [ROLE_FEDERATION_GROUPADMIN, ROLE_FEDERATION_ALUMNUS, ROLE_FEDERATION_EXTERNAL, ROLE_FEDERATION_DISPATCHADDRESS, ROLE_FEDERATION_ITSUPPORT]
GROUP_FEDERALBOARD.role_types = [ROLE_FEDERALBOARD_MEMBER, ROLE_FEDERALBOARD_PRESIDENT, ROLE_FEDERALBOARD_GROUPADMIN, ROLE_FEDERALBOARD_ALUMNUS, ROLE_FEDERALBOARD_EXTERNAL, ROLE_FEDERALBOARD_DISPATCHADDRESS, ROLE_FEDERALBOARD_TREASURER]
GROUP_ORGANIZATIONBOARD.role_types = [ROLE_ORGANIZATIONBOARD_LEADER, ROLE_ORGANIZATIONBOARD_TREASURER, ROLE_ORGANIZATIONBOARD_MEMBER, ROLE_ORGANIZATIONBOARD_GROUPADMIN, ROLE_ORGANIZATIONBOARD_ALUMNUS, ROLE_ORGANIZATIONBOARD_EXTERNAL, ROLE_ORGANIZATIONBOARD_DISPATCHADDRESS]
GROUP_FEDERALPROFESSIONALGROUP.role_types = [ROLE_FEDERALPROFESSIONALGROUP_LEADER, ROLE_FEDERALPROFESSIONALGROUP_MEMBER, ROLE_FEDERALPROFESSIONALGROUP_GROUPADMIN, ROLE_FEDERALPROFESSIONALGROUP_ALUMNUS, ROLE_FEDERALPROFESSIONALGROUP_EXTERNAL, ROLE_FEDERALPROFESSIONALGROUP_DISPATCHADDRESS, ROLE_FEDERALPROFESSIONALGROUP_TREASURER]
GROUP_FEDERALWORKGROUP.role_types = [ROLE_FEDERALWORKGROUP_LEADER, ROLE_FEDERALWORKGROUP_MEMBER, ROLE_FEDERALWORKGROUP_GROUPADMIN, ROLE_FEDERALWORKGROUP_ALUMNUS, ROLE_FEDERALWORKGROUP_EXTERNAL, ROLE_FEDERALWORKGROUP_DISPATCHADDRESS, ROLE_FEDERALWORKGROUP_TREASURER]
GROUP_FEDERALALUMNUSGROUP.role_types = [ROLE_FEDERALALUMNUSGROUP_LEADER, ROLE_FEDERALALUMNUSGROUP_GROUPADMIN, ROLE_FEDERALALUMNUSGROUP_TREASURER, ROLE_FEDERALALUMNUSGROUP_MEMBER, ROLE_FEDERALALUMNUSGROUP_EXTERNAL, ROLE_FEDERALALUMNUSGROUP_DISPATCHADDRESS]
GROUP_STATE.role_types = [ROLE_STATE_COACH, ROLE_STATE_GROUPADMIN, ROLE_STATE_ALUMNUS, ROLE_STATE_EXTERNAL, ROLE_STATE_DISPATCHADDRESS]
GROUP_STATEAGENCY.role_types = [ROLE_STATEAGENCY_LEADER, ROLE_STATEAGENCY_GROUPADMIN, ROLE_STATEAGENCY_ALUMNUS, ROLE_STATEAGENCY_EXTERNAL, ROLE_STATEAGENCY_DISPATCHADDRESS]
GROUP_STATEBOARD.role_types = [ROLE_STATEBOARD_LEADER, ROLE_STATEBOARD_MEMBER, ROLE_STATEBOARD_SUPERVISOR, ROLE_STATEBOARD_PRESIDENT, ROLE_STATEBOARD_GROUPADMIN, ROLE_STATEBOARD_ALUMNUS, ROLE_STATEBOARD_EXTERNAL, ROLE_STATEBOARD_DISPATCHADDRESS]
GROUP_STATEPROFESSIONALGROUP.role_types = [ROLE_STATEPROFESSIONALGROUP_LEADER, ROLE_STATEPROFESSIONALGROUP_MEMBER, ROLE_STATEPROFESSIONALGROUP_GROUPADMIN, ROLE_STATEPROFESSIONALGROUP_ALUMNUS, ROLE_STATEPROFESSIONALGROUP_EXTERNAL, ROLE_STATEPROFESSIONALGROUP_DISPATCHADDRESS]
GROUP_STATEWORKGROUP.role_types = [ROLE_STATEWORKGROUP_LEADER, ROLE_STATEWORKGROUP_MEMBER, ROLE_STATEWORKGROUP_GROUPADMIN, ROLE_STATEWORKGROUP_ALUMNUS, ROLE_STATEWORKGROUP_EXTERNAL, ROLE_STATEWORKGROUP_DISPATCHADDRESS]
GROUP_STATEALUMNUSGROUP.role_types = [ROLE_STATEALUMNUSGROUP_LEADER, ROLE_STATEALUMNUSGROUP_GROUPADMIN, ROLE_STATEALUMNUSGROUP_TREASURER, ROLE_STATEALUMNUSGROUP_MEMBER, ROLE_STATEALUMNUSGROUP_EXTERNAL, ROLE_STATEALUMNUSGROUP_DISPATCHADDRESS]
GROUP_REGION.role_types = [ROLE_REGION_COACH, ROLE_REGION_GROUPADMIN, ROLE_REGION_ALUMNUS, ROLE_REGION_EXTERNAL, ROLE_REGION_DISPATCHADDRESS]
GROUP_REGIONALBOARD.role_types = [ROLE_REGIONALBOARD_LEADER, ROLE_REGIONALBOARD_MEMBER, ROLE_REGIONALBOARD_PRESIDENT, ROLE_REGIONALBOARD_GROUPADMIN, ROLE_REGIONALBOARD_ALUMNUS, ROLE_REGIONALBOARD_EXTERNAL, ROLE_REGIONALBOARD_DISPATCHADDRESS]
GROUP_REGIONALPROFESSIONALGROUP.role_types = [ROLE_REGIONALPROFESSIONALGROUP_LEADER, ROLE_REGIONALPROFESSIONALGROUP_MEMBER, ROLE_REGIONALPROFESSIONALGROUP_GROUPADMIN, ROLE_REGIONALPROFESSIONALGROUP_ALUMNUS, ROLE_REGIONALPROFESSIONALGROUP_EXTERNAL, ROLE_REGIONALPROFESSIONALGROUP_DISPATCHADDRESS]
GROUP_REGIONALWORKGROUP.role_types = [ROLE_REGIONALWORKGROUP_LEADER, ROLE_REGIONALWORKGROUP_MEMBER, ROLE_REGIONALWORKGROUP_GROUPADMIN, ROLE_REGIONALWORKGROUP_ALUMNUS, ROLE_REGIONALWORKGROUP_EXTERNAL, ROLE_REGIONALWORKGROUP_DISPATCHADDRESS]
GROUP_REGIONALALUMNUSGROUP.role_types = [ROLE_REGIONALALUMNUSGROUP_LEADER, ROLE_REGIONALALUMNUSGROUP_GROUPADMIN, ROLE_REGIONALALUMNUSGROUP_TREASURER, ROLE_REGIONALALUMNUSGROUP_MEMBER, ROLE_REGIONALALUMNUSGROUP_EXTERNAL, ROLE_REGIONALALUMNUSGROUP_DISPATCHADDRESS]
GROUP_FLOCK.role_types = [ROLE_FLOCK_LEADER, ROLE_FLOCK_CAMPLEADER, ROLE_FLOCK_PRESIDENT, ROLE_FLOCK_TREASURER, ROLE_FLOCK_GUIDE, ROLE_FLOCK_GROUPADMIN, ROLE_FLOCK_ALUMNUS, ROLE_FLOCK_EXTERNAL, ROLE_FLOCK_DISPATCHADDRESS]
GROUP_CHILDGROUP.role_types = [ROLE_CHILDGROUP_LEADER, ROLE_CHILDGROUP_CHILD, ROLE_CHILDGROUP_GROUPADMIN, ROLE_CHILDGROUP_ALUMNUS, ROLE_CHILDGROUP_EXTERNAL, ROLE_CHILDGROUP_DISPATCHADDRESS]
GROUP_FLOCKALUMNUSGROUP.role_types = [ROLE_FLOCKALUMNUSGROUP_LEADER, ROLE_FLOCKALUMNUSGROUP_GROUPADMIN, ROLE_FLOCKALUMNUSGROUP_TREASURER, ROLE_FLOCKALUMNUSGROUP_MEMBER, ROLE_FLOCKALUMNUSGROUP_EXTERNAL, ROLE_FLOCKALUMNUSGROUP_DISPATCHADDRESS]
GROUP_NEJB.role_types = [ROLE_NEJB_GROUPADMIN, ROLE_NEJB_DISPATCHADDRESS, ROLE_NEJB_ITSUPPORT]
GROUP_NEJBBUNDESLEITUNG.role_types = [ROLE_NEJBBUNDESLEITUNG_GROUPADMIN]
GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING.role_types = [ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_LEADER, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_GROUPADMIN, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_TREASURER, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_ACTIVEMEMBER, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_PASSIVEMEMBER, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_COLLECTIVEMEMBER, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_NEJBJOINER, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_EXTERNAL, ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_DISPATCHADDRESS]
GROUP_NEJBKANTON.role_types = [ROLE_NEJBKANTON_GROUPADMIN]
GROUP_KANTONEHEMALIGENVEREIN.role_types = [ROLE_KANTONEHEMALIGENVEREIN_LEADER, ROLE_KANTONEHEMALIGENVEREIN_GROUPADMIN, ROLE_KANTONEHEMALIGENVEREIN_TREASURER, ROLE_KANTONEHEMALIGENVEREIN_NEJBMEMBER, ROLE_KANTONEHEMALIGENVEREIN_NEJBJOINER, ROLE_KANTONEHEMALIGENVEREIN_EXTERNAL, ROLE_KANTONEHEMALIGENVEREIN_DISPATCHADDRESS]
GROUP_NEJBREGION.role_types = [ROLE_NEJBREGION_GROUPADMIN]
GROUP_REGIONEHEMALIGENVEREIN.role_types = [ROLE_REGIONEHEMALIGENVEREIN_LEADER, ROLE_REGIONEHEMALIGENVEREIN_GROUPADMIN, ROLE_REGIONEHEMALIGENVEREIN_TREASURER, ROLE_REGIONEHEMALIGENVEREIN_NEJBMEMBER, ROLE_REGIONEHEMALIGENVEREIN_NEJBJOINER, ROLE_REGIONEHEMALIGENVEREIN_EXTERNAL, ROLE_REGIONEHEMALIGENVEREIN_DISPATCHADDRESS]
GROUP_NEJBSCHAR.role_types = [ROLE_NEJBSCHAR_LEADER, ROLE_NEJBSCHAR_GROUPADMIN, ROLE_NEJBSCHAR_TREASURER, ROLE_NEJBSCHAR_NEJBMEMBER, ROLE_NEJBSCHAR_NEJBJOINER, ROLE_NEJBSCHAR_EXTERNAL, ROLE_NEJBSCHAR_DISPATCHADDRESS]
GROUP_SIMPLEGROUP.role_types = [ROLE_SIMPLEGROUP_LEADER, ROLE_SIMPLEGROUP_MEMBER, ROLE_SIMPLEGROUP_GROUPADMIN, ROLE_SIMPLEGROUP_ALUMNUS, ROLE_SIMPLEGROUP_EXTERNAL, ROLE_SIMPLEGROUP_DISPATCHADDRESS]
GROUP_NEJBSIMPLEGROUP.role_types = [ROLE_NEJBSIMPLEGROUP_LEADER, ROLE_NEJBSIMPLEGROUP_MEMBER, ROLE_NEJBSIMPLEGROUP_GROUPADMIN, ROLE_NEJBSIMPLEGROUP_EXTERNAL, ROLE_NEJBSIMPLEGROUP_DISPATCHADDRESS, ROLE_NEJBSIMPLEGROUP_NEWJOINER]

ALL_GROUPS = {
    "Group::Root": GROUP_ROOT,
    "Group::Federation": GROUP_FEDERATION,
    "Group::FederalBoard": GROUP_FEDERALBOARD,
    "Group::OrganizationBoard": GROUP_ORGANIZATIONBOARD,
    "Group::FederalProfessionalGroup": GROUP_FEDERALPROFESSIONALGROUP,
    "Group::FederalWorkGroup": GROUP_FEDERALWORKGROUP,
    "Group::FederalAlumnusGroup": GROUP_FEDERALALUMNUSGROUP,
    "Group::State": GROUP_STATE,
    "Group::StateAgency": GROUP_STATEAGENCY,
    "Group::StateBoard": GROUP_STATEBOARD,
    "Group::StateProfessionalGroup": GROUP_STATEPROFESSIONALGROUP,
    "Group::StateWorkGroup": GROUP_STATEWORKGROUP,
    "Group::StateAlumnusGroup": GROUP_STATEALUMNUSGROUP,
    "Group::Region": GROUP_REGION,
    "Group::RegionalBoard": GROUP_REGIONALBOARD,
    "Group::RegionalProfessionalGroup": GROUP_REGIONALPROFESSIONALGROUP,
    "Group::RegionalWorkGroup": GROUP_REGIONALWORKGROUP,
    "Group::RegionalAlumnusGroup": GROUP_REGIONALALUMNUSGROUP,
    "Group::Flock": GROUP_FLOCK,
    "Group::ChildGroup": GROUP_CHILDGROUP,
    "Group::FlockAlumnusGroup": GROUP_FLOCKALUMNUSGROUP,
    "Group::Nejb": GROUP_NEJB,
    "Group::NejbBundesleitung": GROUP_NEJBBUNDESLEITUNG,
    "Group::NetzwerkEhemaligeJungwachtBlauring": GROUP_NETZWERKEHEMALIGEJUNGWACHTBLAURING,
    "Group::NejbKanton": GROUP_NEJBKANTON,
    "Group::KantonEhemaligenverein": GROUP_KANTONEHEMALIGENVEREIN,
    "Group::NejbRegion": GROUP_NEJBREGION,
    "Group::RegionEhemaligenverein": GROUP_REGIONEHEMALIGENVEREIN,
    "Group::NejbSchar": GROUP_NEJBSCHAR,
    "Group::SimpleGroup": GROUP_SIMPLEGROUP,
    "Group::NejbSimpleGroup": GROUP_NEJBSIMPLEGROUP,
}

ALL_ROLES = {
    "Group::Root::Admin": ROLE_ROOT_ADMIN,
    "Group::Federation::GroupAdmin": ROLE_FEDERATION_GROUPADMIN,
    "Group::Federation::Alumnus": ROLE_FEDERATION_ALUMNUS,
    "Group::Federation::External": ROLE_FEDERATION_EXTERNAL,
    "Group::Federation::DispatchAddress": ROLE_FEDERATION_DISPATCHADDRESS,
    "Group::Federation::ItSupport": ROLE_FEDERATION_ITSUPPORT,
    "Group::FederalBoard::Member": ROLE_FEDERALBOARD_MEMBER,
    "Group::FederalBoard::President": ROLE_FEDERALBOARD_PRESIDENT,
    "Group::FederalBoard::GroupAdmin": ROLE_FEDERALBOARD_GROUPADMIN,
    "Group::FederalBoard::Alumnus": ROLE_FEDERALBOARD_ALUMNUS,
    "Group::FederalBoard::External": ROLE_FEDERALBOARD_EXTERNAL,
    "Group::FederalBoard::DispatchAddress": ROLE_FEDERALBOARD_DISPATCHADDRESS,
    "Group::FederalBoard::Treasurer": ROLE_FEDERALBOARD_TREASURER,
    "Group::OrganizationBoard::Leader": ROLE_ORGANIZATIONBOARD_LEADER,
    "Group::OrganizationBoard::Treasurer": ROLE_ORGANIZATIONBOARD_TREASURER,
    "Group::OrganizationBoard::Member": ROLE_ORGANIZATIONBOARD_MEMBER,
    "Group::OrganizationBoard::GroupAdmin": ROLE_ORGANIZATIONBOARD_GROUPADMIN,
    "Group::OrganizationBoard::Alumnus": ROLE_ORGANIZATIONBOARD_ALUMNUS,
    "Group::OrganizationBoard::External": ROLE_ORGANIZATIONBOARD_EXTERNAL,
    "Group::OrganizationBoard::DispatchAddress": ROLE_ORGANIZATIONBOARD_DISPATCHADDRESS,
    "Group::FederalProfessionalGroup::Leader": ROLE_FEDERALPROFESSIONALGROUP_LEADER,
    "Group::FederalProfessionalGroup::Member": ROLE_FEDERALPROFESSIONALGROUP_MEMBER,
    "Group::FederalProfessionalGroup::GroupAdmin": ROLE_FEDERALPROFESSIONALGROUP_GROUPADMIN,
    "Group::FederalProfessionalGroup::Alumnus": ROLE_FEDERALPROFESSIONALGROUP_ALUMNUS,
    "Group::FederalProfessionalGroup::External": ROLE_FEDERALPROFESSIONALGROUP_EXTERNAL,
    "Group::FederalProfessionalGroup::DispatchAddress": ROLE_FEDERALPROFESSIONALGROUP_DISPATCHADDRESS,
    "Group::FederalProfessionalGroup::Treasurer": ROLE_FEDERALPROFESSIONALGROUP_TREASURER,
    "Group::FederalWorkGroup::Leader": ROLE_FEDERALWORKGROUP_LEADER,
    "Group::FederalWorkGroup::Member": ROLE_FEDERALWORKGROUP_MEMBER,
    "Group::FederalWorkGroup::GroupAdmin": ROLE_FEDERALWORKGROUP_GROUPADMIN,
    "Group::FederalWorkGroup::Alumnus": ROLE_FEDERALWORKGROUP_ALUMNUS,
    "Group::FederalWorkGroup::External": ROLE_FEDERALWORKGROUP_EXTERNAL,
    "Group::FederalWorkGroup::DispatchAddress": ROLE_FEDERALWORKGROUP_DISPATCHADDRESS,
    "Group::FederalWorkGroup::Treasurer": ROLE_FEDERALWORKGROUP_TREASURER,
    "Group::FederalAlumnusGroup::Leader": ROLE_FEDERALALUMNUSGROUP_LEADER,
    "Group::FederalAlumnusGroup::GroupAdmin": ROLE_FEDERALALUMNUSGROUP_GROUPADMIN,
    "Group::FederalAlumnusGroup::Treasurer": ROLE_FEDERALALUMNUSGROUP_TREASURER,
    "Group::FederalAlumnusGroup::Member": ROLE_FEDERALALUMNUSGROUP_MEMBER,
    "Group::FederalAlumnusGroup::External": ROLE_FEDERALALUMNUSGROUP_EXTERNAL,
    "Group::FederalAlumnusGroup::DispatchAddress": ROLE_FEDERALALUMNUSGROUP_DISPATCHADDRESS,
    "Group::State::Coach": ROLE_STATE_COACH,
    "Group::State::GroupAdmin": ROLE_STATE_GROUPADMIN,
    "Group::State::Alumnus": ROLE_STATE_ALUMNUS,
    "Group::State::External": ROLE_STATE_EXTERNAL,
    "Group::State::DispatchAddress": ROLE_STATE_DISPATCHADDRESS,
    "Group::StateAgency::Leader": ROLE_STATEAGENCY_LEADER,
    "Group::StateAgency::GroupAdmin": ROLE_STATEAGENCY_GROUPADMIN,
    "Group::StateAgency::Alumnus": ROLE_STATEAGENCY_ALUMNUS,
    "Group::StateAgency::External": ROLE_STATEAGENCY_EXTERNAL,
    "Group::StateAgency::DispatchAddress": ROLE_STATEAGENCY_DISPATCHADDRESS,
    "Group::StateBoard::Leader": ROLE_STATEBOARD_LEADER,
    "Group::StateBoard::Member": ROLE_STATEBOARD_MEMBER,
    "Group::StateBoard::Supervisor": ROLE_STATEBOARD_SUPERVISOR,
    "Group::StateBoard::President": ROLE_STATEBOARD_PRESIDENT,
    "Group::StateBoard::GroupAdmin": ROLE_STATEBOARD_GROUPADMIN,
    "Group::StateBoard::Alumnus": ROLE_STATEBOARD_ALUMNUS,
    "Group::StateBoard::External": ROLE_STATEBOARD_EXTERNAL,
    "Group::StateBoard::DispatchAddress": ROLE_STATEBOARD_DISPATCHADDRESS,
    "Group::StateProfessionalGroup::Leader": ROLE_STATEPROFESSIONALGROUP_LEADER,
    "Group::StateProfessionalGroup::Member": ROLE_STATEPROFESSIONALGROUP_MEMBER,
    "Group::StateProfessionalGroup::GroupAdmin": ROLE_STATEPROFESSIONALGROUP_GROUPADMIN,
    "Group::StateProfessionalGroup::Alumnus": ROLE_STATEPROFESSIONALGROUP_ALUMNUS,
    "Group::StateProfessionalGroup::External": ROLE_STATEPROFESSIONALGROUP_EXTERNAL,
    "Group::StateProfessionalGroup::DispatchAddress": ROLE_STATEPROFESSIONALGROUP_DISPATCHADDRESS,
    "Group::StateWorkGroup::Leader": ROLE_STATEWORKGROUP_LEADER,
    "Group::StateWorkGroup::Member": ROLE_STATEWORKGROUP_MEMBER,
    "Group::StateWorkGroup::GroupAdmin": ROLE_STATEWORKGROUP_GROUPADMIN,
    "Group::StateWorkGroup::Alumnus": ROLE_STATEWORKGROUP_ALUMNUS,
    "Group::StateWorkGroup::External": ROLE_STATEWORKGROUP_EXTERNAL,
    "Group::StateWorkGroup::DispatchAddress": ROLE_STATEWORKGROUP_DISPATCHADDRESS,
    "Group::StateAlumnusGroup::Leader": ROLE_STATEALUMNUSGROUP_LEADER,
    "Group::StateAlumnusGroup::GroupAdmin": ROLE_STATEALUMNUSGROUP_GROUPADMIN,
    "Group::StateAlumnusGroup::Treasurer": ROLE_STATEALUMNUSGROUP_TREASURER,
    "Group::StateAlumnusGroup::Member": ROLE_STATEALUMNUSGROUP_MEMBER,
    "Group::StateAlumnusGroup::External": ROLE_STATEALUMNUSGROUP_EXTERNAL,
    "Group::StateAlumnusGroup::DispatchAddress": ROLE_STATEALUMNUSGROUP_DISPATCHADDRESS,
    "Group::Region::Coach": ROLE_REGION_COACH,
    "Group::Region::GroupAdmin": ROLE_REGION_GROUPADMIN,
    "Group::Region::Alumnus": ROLE_REGION_ALUMNUS,
    "Group::Region::External": ROLE_REGION_EXTERNAL,
    "Group::Region::DispatchAddress": ROLE_REGION_DISPATCHADDRESS,
    "Group::RegionalBoard::Leader": ROLE_REGIONALBOARD_LEADER,
    "Group::RegionalBoard::Member": ROLE_REGIONALBOARD_MEMBER,
    "Group::RegionalBoard::President": ROLE_REGIONALBOARD_PRESIDENT,
    "Group::RegionalBoard::GroupAdmin": ROLE_REGIONALBOARD_GROUPADMIN,
    "Group::RegionalBoard::Alumnus": ROLE_REGIONALBOARD_ALUMNUS,
    "Group::RegionalBoard::External": ROLE_REGIONALBOARD_EXTERNAL,
    "Group::RegionalBoard::DispatchAddress": ROLE_REGIONALBOARD_DISPATCHADDRESS,
    "Group::RegionalProfessionalGroup::Leader": ROLE_REGIONALPROFESSIONALGROUP_LEADER,
    "Group::RegionalProfessionalGroup::Member": ROLE_REGIONALPROFESSIONALGROUP_MEMBER,
    "Group::RegionalProfessionalGroup::GroupAdmin": ROLE_REGIONALPROFESSIONALGROUP_GROUPADMIN,
    "Group::RegionalProfessionalGroup::Alumnus": ROLE_REGIONALPROFESSIONALGROUP_ALUMNUS,
    "Group::RegionalProfessionalGroup::External": ROLE_REGIONALPROFESSIONALGROUP_EXTERNAL,
    "Group::RegionalProfessionalGroup::DispatchAddress": ROLE_REGIONALPROFESSIONALGROUP_DISPATCHADDRESS,
    "Group::RegionalWorkGroup::Leader": ROLE_REGIONALWORKGROUP_LEADER,
    "Group::RegionalWorkGroup::Member": ROLE_REGIONALWORKGROUP_MEMBER,
    "Group::RegionalWorkGroup::GroupAdmin": ROLE_REGIONALWORKGROUP_GROUPADMIN,
    "Group::RegionalWorkGroup::Alumnus": ROLE_REGIONALWORKGROUP_ALUMNUS,
    "Group::RegionalWorkGroup::External": ROLE_REGIONALWORKGROUP_EXTERNAL,
    "Group::RegionalWorkGroup::DispatchAddress": ROLE_REGIONALWORKGROUP_DISPATCHADDRESS,
    "Group::RegionalAlumnusGroup::Leader": ROLE_REGIONALALUMNUSGROUP_LEADER,
    "Group::RegionalAlumnusGroup::GroupAdmin": ROLE_REGIONALALUMNUSGROUP_GROUPADMIN,
    "Group::RegionalAlumnusGroup::Treasurer": ROLE_REGIONALALUMNUSGROUP_TREASURER,
    "Group::RegionalAlumnusGroup::Member": ROLE_REGIONALALUMNUSGROUP_MEMBER,
    "Group::RegionalAlumnusGroup::External": ROLE_REGIONALALUMNUSGROUP_EXTERNAL,
    "Group::RegionalAlumnusGroup::DispatchAddress": ROLE_REGIONALALUMNUSGROUP_DISPATCHADDRESS,
    "Group::Flock::Leader": ROLE_FLOCK_LEADER,
    "Group::Flock::CampLeader": ROLE_FLOCK_CAMPLEADER,
    "Group::Flock::President": ROLE_FLOCK_PRESIDENT,
    "Group::Flock::Treasurer": ROLE_FLOCK_TREASURER,
    "Group::Flock::Guide": ROLE_FLOCK_GUIDE,
    "Group::Flock::GroupAdmin": ROLE_FLOCK_GROUPADMIN,
    "Group::Flock::Alumnus": ROLE_FLOCK_ALUMNUS,
    "Group::Flock::External": ROLE_FLOCK_EXTERNAL,
    "Group::Flock::DispatchAddress": ROLE_FLOCK_DISPATCHADDRESS,
    "Group::ChildGroup::Leader": ROLE_CHILDGROUP_LEADER,
    "Group::ChildGroup::Child": ROLE_CHILDGROUP_CHILD,
    "Group::ChildGroup::GroupAdmin": ROLE_CHILDGROUP_GROUPADMIN,
    "Group::ChildGroup::Alumnus": ROLE_CHILDGROUP_ALUMNUS,
    "Group::ChildGroup::External": ROLE_CHILDGROUP_EXTERNAL,
    "Group::ChildGroup::DispatchAddress": ROLE_CHILDGROUP_DISPATCHADDRESS,
    "Group::FlockAlumnusGroup::Leader": ROLE_FLOCKALUMNUSGROUP_LEADER,
    "Group::FlockAlumnusGroup::GroupAdmin": ROLE_FLOCKALUMNUSGROUP_GROUPADMIN,
    "Group::FlockAlumnusGroup::Treasurer": ROLE_FLOCKALUMNUSGROUP_TREASURER,
    "Group::FlockAlumnusGroup::Member": ROLE_FLOCKALUMNUSGROUP_MEMBER,
    "Group::FlockAlumnusGroup::External": ROLE_FLOCKALUMNUSGROUP_EXTERNAL,
    "Group::FlockAlumnusGroup::DispatchAddress": ROLE_FLOCKALUMNUSGROUP_DISPATCHADDRESS,
    "Group::Nejb::GroupAdmin": ROLE_NEJB_GROUPADMIN,
    "Group::Nejb::DispatchAddress": ROLE_NEJB_DISPATCHADDRESS,
    "Group::Nejb::ITSupport": ROLE_NEJB_ITSUPPORT,
    "Group::NejbBundesleitung::GroupAdmin": ROLE_NEJBBUNDESLEITUNG_GROUPADMIN,
    "Group::NetzwerkEhemaligeJungwachtBlauring::Leader": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_LEADER,
    "Group::NetzwerkEhemaligeJungwachtBlauring::GroupAdmin": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_GROUPADMIN,
    "Group::NetzwerkEhemaligeJungwachtBlauring::Treasurer": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_TREASURER,
    "Group::NetzwerkEhemaligeJungwachtBlauring::ActiveMember": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_ACTIVEMEMBER,
    "Group::NetzwerkEhemaligeJungwachtBlauring::PassiveMember": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_PASSIVEMEMBER,
    "Group::NetzwerkEhemaligeJungwachtBlauring::CollectiveMember": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_COLLECTIVEMEMBER,
    "Group::NetzwerkEhemaligeJungwachtBlauring::NejbJoiner": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_NEJBJOINER,
    "Group::NetzwerkEhemaligeJungwachtBlauring::External": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_EXTERNAL,
    "Group::NetzwerkEhemaligeJungwachtBlauring::DispatchAddress": ROLE_NETZWERKEHEMALIGEJUNGWACHTBLAURING_DISPATCHADDRESS,
    "Group::NejbKanton::GroupAdmin": ROLE_NEJBKANTON_GROUPADMIN,
    "Group::KantonEhemaligenverein::Leader": ROLE_KANTONEHEMALIGENVEREIN_LEADER,
    "Group::KantonEhemaligenverein::GroupAdmin": ROLE_KANTONEHEMALIGENVEREIN_GROUPADMIN,
    "Group::KantonEhemaligenverein::Treasurer": ROLE_KANTONEHEMALIGENVEREIN_TREASURER,
    "Group::KantonEhemaligenverein::NejbMember": ROLE_KANTONEHEMALIGENVEREIN_NEJBMEMBER,
    "Group::KantonEhemaligenverein::NejbJoiner": ROLE_KANTONEHEMALIGENVEREIN_NEJBJOINER,
    "Group::KantonEhemaligenverein::External": ROLE_KANTONEHEMALIGENVEREIN_EXTERNAL,
    "Group::KantonEhemaligenverein::DispatchAddress": ROLE_KANTONEHEMALIGENVEREIN_DISPATCHADDRESS,
    "Group::NejbRegion::GroupAdmin": ROLE_NEJBREGION_GROUPADMIN,
    "Group::RegionEhemaligenverein::Leader": ROLE_REGIONEHEMALIGENVEREIN_LEADER,
    "Group::RegionEhemaligenverein::GroupAdmin": ROLE_REGIONEHEMALIGENVEREIN_GROUPADMIN,
    "Group::RegionEhemaligenverein::Treasurer": ROLE_REGIONEHEMALIGENVEREIN_TREASURER,
    "Group::RegionEhemaligenverein::NejbMember": ROLE_REGIONEHEMALIGENVEREIN_NEJBMEMBER,
    "Group::RegionEhemaligenverein::NejbJoiner": ROLE_REGIONEHEMALIGENVEREIN_NEJBJOINER,
    "Group::RegionEhemaligenverein::External": ROLE_REGIONEHEMALIGENVEREIN_EXTERNAL,
    "Group::RegionEhemaligenverein::DispatchAddress": ROLE_REGIONEHEMALIGENVEREIN_DISPATCHADDRESS,
    "Group::NejbSchar::Leader": ROLE_NEJBSCHAR_LEADER,
    "Group::NejbSchar::GroupAdmin": ROLE_NEJBSCHAR_GROUPADMIN,
    "Group::NejbSchar::Treasurer": ROLE_NEJBSCHAR_TREASURER,
    "Group::NejbSchar::NejbMember": ROLE_NEJBSCHAR_NEJBMEMBER,
    "Group::NejbSchar::NejbJoiner": ROLE_NEJBSCHAR_NEJBJOINER,
    "Group::NejbSchar::External": ROLE_NEJBSCHAR_EXTERNAL,
    "Group::NejbSchar::DispatchAddress": ROLE_NEJBSCHAR_DISPATCHADDRESS,
    "Group::SimpleGroup::Leader": ROLE_SIMPLEGROUP_LEADER,
    "Group::SimpleGroup::Member": ROLE_SIMPLEGROUP_MEMBER,
    "Group::SimpleGroup::GroupAdmin": ROLE_SIMPLEGROUP_GROUPADMIN,
    "Group::SimpleGroup::Alumnus": ROLE_SIMPLEGROUP_ALUMNUS,
    "Group::SimpleGroup::External": ROLE_SIMPLEGROUP_EXTERNAL,
    "Group::SimpleGroup::DispatchAddress": ROLE_SIMPLEGROUP_DISPATCHADDRESS,
    "Group::NejbSimpleGroup::Leader": ROLE_NEJBSIMPLEGROUP_LEADER,
    "Group::NejbSimpleGroup::Member": ROLE_NEJBSIMPLEGROUP_MEMBER,
    "Group::NejbSimpleGroup::GroupAdmin": ROLE_NEJBSIMPLEGROUP_GROUPADMIN,
    "Group::NejbSimpleGroup::External": ROLE_NEJBSIMPLEGROUP_EXTERNAL,
    "Group::NejbSimpleGroup::DispatchAddress": ROLE_NEJBSIMPLEGROUP_DISPATCHADDRESS,
    "Group::NejbSimpleGroup::NewJoiner": ROLE_NEJBSIMPLEGROUP_NEWJOINER,
}
