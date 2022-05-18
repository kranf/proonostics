from datetime import datetime
from source import settings
import pymongo
from source.model import Race


class ScrappedDataService:

    def __init__(self, mongo_db):
        self.mongo_db = mongo_db
        self._create_indexes()

    def _create_indexes(self):
        self.mongo_db.programs.create_index([("date_string", pymongo.ASCENDING)], unique=True)
        self.mongo_db.participants.create_index([("race_id", pymongo.ASCENDING)], unique=True)
        self.mongo_db.participants_detailed_perf.create_index([("race_id", pymongo.ASCENDING)], unique=True)

    def get_latest_scrapping(self):
        date_latest = self.mongo_db.latest_scrapping.find_one()["latest"]
        return datetime.strptime(date_latest, settings.DATE_FORMAT).date()

    def set_latest_scrapping(self, _date):
        self.mongo_db.latest_scrapping.delete_many({})
        return self.mongo_db.latest_scrapping.insert_one({"latest": _date.strftime(settings.DATE_FORMAT)})

    def save_program(self, program, date_string):
        """ :param: date_string ddMMYYYY date of the program"""
        program["date_string"] = date_string
        return self.mongo_db.programs.insert_one(program)

    def save_participants(self, participants, date, meeting_id, race_id):
        participants["race_id"] = "{}R{}C{}".format(date, meeting_id, race_id)
        return self.mongo_db.participants.insert_one(participants)

    def save_participants_detailed_perf(self, participants_detailed_perf, date, meeting_id, race_id):
        participants_detailed_perf["race_id"] = "{}R{}C{}".format(date, meeting_id, race_id)
        return self.mongo_db.participants_detailed_perf.insert_one(participants_detailed_perf)

    def get_all_programs(self):
        return self.mongo_db.programs.find()

    def get_races_by_date(self, date_string):
        """ :param date_string ddMMYYYY date of the program"""
        program = self.mongo_db.programs.find_one({"date_string": date_string})
        races = []
        for meeting in program['reunions']:
            for race in meeting['courses']:
                races.append(Race.fromJson(race, meeting))
        meetings = [meeting for meeting in program['reunions']]
        races = [race for race in meeting]
        return [Race.fromJson(race, meeting) for meeting in program['reunions'] for race in meeting['courses']]