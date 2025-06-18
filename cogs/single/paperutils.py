from typing import List, Literal
import io  # Added for BytesIO
import re

from discord.ext.commands import Cog
from discord import Interaction, File as dFile, ButtonStyle
from discord.ui import Button, View, DynamicItem
from discord.app_commands import command, describe, autocomplete, choices, Choice
# from discord.app_commands import Choice

import logging; from logger import create_console_handler, create_file_handler
from main import PPBdpy
import random, aiohttp
from io import BytesIO  
# import asyncio, 
# import time

class Subject:
    """Data structure for storing subject information."""
    def __init__(self, full_subjectID: str, short_subjectID: str, 
                 seasons: dict, years: range, rand_years: range, papers: List[tuple], season_specific_papers: dict = None):
        self.full_subjectID = full_subjectID
        self.short_subjectID = short_subjectID
        self.seasons = seasons
        self.years = years
        self.rand_years = rand_years
        self.papers = papers
        self.season_specific_papers = season_specific_papers or {}

class BestExamHelpIO:
    """Data structure for storing past paper.
    
    Data are used for random paper generation / season conversion only, please do HTTP checks on requests if user requests a specific paper."""
    # Subject: Further Mathematics (9231)
    FURTHER_MATH = Subject(
        full_subjectID="mathematics-further-9231",
        short_subjectID="9231",
        seasons={
            "jun": "s",
            "nov": "w"
        },
        years=range(2010, 2024+1),
        rand_years=range(2010, 2024+1),
        papers=[
            (range(2010, 2019+1), [11, 12, 13, 21, 22, 23]),
            (range(2020, 2024+1), [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43])
        ]
    )
    # Subject: Mathematics (9709)
    MATH = Subject(
        full_subjectID="mathematics-9709",
        short_subjectID="9709",
        seasons={
            "march": "m",
            "jun": "s",
            "nov": "w"
        },
        years=range(2010, 2024+1),
        rand_years=range(2016, 2024+1),
        papers=[
            (range(2010, 2024+1), [int(a*10+b) for a in range(1, 7+1) for b in range(1, 3+1)])
        ],
        season_specific_papers={
            "m": [
                (range(2016, 2024+1), [int(a*10+2) for a in range(1, 7+1)])
            ]
        }
    )
    # Subject: Chemistry (9701)
    CHEMISTRY = Subject(
        full_subjectID="chemistry-9701",
        short_subjectID="9701",
        seasons={
            "march": "m",
            "jun": "s",
            "nov": "w"
        },
        years=range(2010, 2024+1),
        rand_years=range(2016, 2024+1),
        papers=[
            (range(2010, 2024+1), [int(a*10+b) for a in range(1, 5+1) for b in range(1, 3+1)])
        ],
        season_specific_papers={
            "m": [
                (range(2016, 2024+1), [int(a*10+2) for a in range(1, 5+1)])
            ]
        }
    )
    # Subject: Physics (9702)
    PHYSICS = Subject(
        full_subjectID="physics-9702",
        short_subjectID="9702",
        seasons={
            "march": "m",
            "jun": "s",
            "nov": "w"
        },
        years=range(2010, 2024+1),
        rand_years=range(2016, 2024+1),
        papers=[
            (range(2010, 2024+1), [int(a*10+b) for a in range(1, 5+1) for b in range(1, 3+1)])
        ],
        season_specific_papers={
            "m": [
                (range(2016, 2024+1), [int(a*10+2) for a in range(1, 5+1)])
            ]
        }
    )
    def get_subject(self, subject: str):
        subjects = {
            "further_math": self.FURTHER_MATH,
            "math": self.MATH,
            "chemistry": self.CHEMISTRY,
            "physics": self.PHYSICS,
        }
        return subjects.get(subject.lower(), None)
    def get_subject_by_short_id(self, short_subjectID: str):
        subjects = {
            "9231": self.FURTHER_MATH,
            "9709": self.MATH,
            "9701": self.CHEMISTRY,
            "9702": self.PHYSICS,
        }
        return subjects.get(short_subjectID, None)
    # https://bestexamhelp.com/exam/cambridge-international-a-level/{full_subjectid}/{year}/{short_subjectid}_{season}{shortyear}_{documenttype}.pdf
    def construct_link(self, subject: Subject, year: int, season: str, documenttype: Literal["qp", "ms"], paper_id: int) -> str:
        short_year = str(year)[-2:]
        return f"https://bestexamhelp.com/exam/cambridge-international-a-level/{subject.full_subjectID}/{year}/{subject.short_subjectID}_{season}{short_year}_{documenttype}_{paper_id}.pdf"

class GetMSfromQP(DynamicItem[Button], template=r'ms_(?P<season>[a-z])(?P<year>\d{2})_(?P<subject_id>\d{4})_(?P<paper_id>\d+)'):
    def __init__(self, subject: Subject, year: int, season: str, paper_id: int):
        
        super().__init__(
            Button(
                style=ButtonStyle.green,
                label="Mark Scheme",
                custom_id=f"ms_{season}{str(year)[-2:]}_{subject.short_subjectID}_{paper_id}"
            )
        )
        self.subject = subject
        self.year = year
        self.season = season
        self.paper_id = paper_id
        self.logger = None
    
    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Button, match: re.Match[str], /):
        season = match['season']
        year = int("20" + match['year'])  # Convert 2-digit to 4-digit year
        subject_id = match['subject_id']
        paper_id = int(match['paper_id'])
        
        subject_obj = BestExamHelpIO().get_subject_by_short_id(subject_id)
        
        if not subject_obj:
            await interaction.response.send_message("Error: Could not find the subject information.", ephemeral=True)
            return None
            
        return cls(subject_obj, year, season, paper_id)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=False)
        link = BestExamHelpIO().construct_link(self.subject, self.year, self.season, "ms", self.paper_id)
        failed = False
        ms_file = None
        text_response = ""
        self.logger = logging.getLogger("cogs.single.paperutils")
        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'PastPaperBot/1.0',
                    'Accept': 'application/pdf'
                }
                async with session.get(link, headers=headers) as response:
                    if response.status == 304 or response.status in range(200, 300):
                        file_content = await response.read()
                        file_bytes = BytesIO(file_content)
                        ms_file = dFile(file_bytes, filename=link.split('/')[-1])
                        text_response = f"Here's your mark scheme: (**{ms_file.filename}**)"
                        self.logger.debug(f"Successfully fetched mark scheme from {link} with status {response.status}")
                    else:
                        text_response = f"Failed to fetch the mark scheme. Status code: {response.status}"
                        failed = True
            except Exception as e:
                self.logger.error(f"Error fetching mark scheme: {e.__class__.__name__}", exc_info=True)
                text_response = f"An error occurred while fetching the mark scheme: {str(e)}"
                failed = True

        if failed:
            await interaction.followup.send(content=text_response)
        elif ms_file is None:
            await interaction.followup.send(content=text_response)
        else:
            await interaction.followup.send(content=text_response, ephemeral=False, file=ms_file)
        # finished request
        self.logger.info(f"Finished request for {interaction.user} with {self.subject.short_subjectID} {self.year} {self.season} {self.paper_id} (Result: {'Success' if ms_file else 'Failed'})")

class PaperUtils(Cog):
    def __init__(self, bot: PPBdpy):
        self.bot = bot
        self.setup_log()
        
    def setup_log(self):
        paperutils_logger = logging.getLogger("cogs.single.paperutils")
        paperutils_logger.setLevel(logging.DEBUG)
        paperutils_logger.addHandler(create_console_handler(logging.INFO))
        paperutils_logger.addHandler(create_file_handler("./logs/cogs/single/paperutils", "paperutils"))
        self.logger = paperutils_logger
    @Cog.listener()
    async def on_ready(self):
        #raise NotImplementedError
        return
    @command(name="qp", description="Get a past paper to work with.")
    @choices(subject=[Choice(name='🔢 | Further Mathematics 9231', value='further_math'), 
                      Choice(name='🧮 | Mathematics 9709', value='math'),
                      Choice(name='🧪 | Chemistry 9701', value='chemistry'),
                      Choice(name='🔬 | Physics 9702', value='physics')])
    @choices(season=[Choice(name='May/June', value='jun'), Choice(name='October/November', value='nov'), Choice(name='February/March', value='march')])
    @describe(subject="Subject you want to get the past paper for.",
                year="Year of the past paper (e.g. 2020, leave blank for random year)",
                season="Season of the past paper (e.g. May/June, October/November, February/March, leave blank for random season)",
                paper_id="ID of the past paper (e.g. 11, -1 for random paper ID)")
    async def qp(self, interaction: Interaction, subject: str, year: int = -1, season: str = "random", paper_id: int = -1):
        await interaction.response.defer(ephemeral=False)
        self.logger.debug(f"Preparing to serve user {interaction.user} with paper {subject} {year} {season} {paper_id}")
        is_randomized = False
        subj = BestExamHelpIO().get_subject(subject)
        if not isinstance(subj, Subject):
            await interaction.followup.send("Invalid subject selected. Please try again.", ephemeral=True)
            return
        if year == -1: # Random year
            year = random.choice(subj.rand_years)
            is_randomized = True
        elif year not in subj.years:
            await interaction.followup.send(f"Invalid year selected. Please choose a year between {subj.years.start} and {subj.years.stop - 1}.", ephemeral=True)
            return
        if season == "random":
            season = random.choice(list(subj.seasons.keys()))
            season = subj.seasons[season]
            is_randomized = True
        else:
            season = season.lower()
            season = subj.seasons.get(season)
            if not season:
                await interaction.followup.send("Invalid season selected. Please choose from May/June, October/November, or February/March.", ephemeral=True)
                return
        if paper_id == -1:
            for cond, pps in subj.papers:
                if year not in cond: continue
                spps = []
                if hasattr(subj, 'season_specific_papers'):
                    if season in subj.season_specific_papers:
                        for cond_, spps_ in subj.season_specific_papers[season]:
                            if year not in cond_: continue
                            spps = spps_
                paper_id = random.choice(pps + spps)
                break
        else:
            for cond, pps in subj.papers:
                if year not in cond: continue
                if paper_id not in pps:
                    await interaction.followup.send(f"Invalid paper ID selected for the year {year}. Please choose a valid paper ID.", ephemeral=True)
                    return
                break
        link = BestExamHelpIO().construct_link(subj, year, season, "qp", paper_id)
        msg = await interaction.followup.send("Attempting to fetch the past paper...", ephemeral=True)
        paper_file = None
        failed = False
        text_response = ""
        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'PastPaperBot/1.0',
                    'Accept': 'application/pdf'
                }
                self.logger.debug(f"Fetching past paper from {link}")
                async with session.get(link, headers=headers) as response:
                    filename = link.split('/')[-1]
                    if response.status == 304 or response.status in range(200, 300):
                        self.logger.debug(f"Successfully fetched past paper from {link} with status {response.status}")
                        self.logger.debug(f"Attempting to create file content for {response.url}")
                        file_content = await response.read()
                        file_bytes = BytesIO(file_content)
                        paper_file = dFile(file_bytes, filename=filename)
                        self.logger.debug(f"Paper file created: {filename}, size: {len(file_content)} bytes")
                        text_response = f"Here's your {'random ' if is_randomized else ''}past paper: (**{filename}**)"
                    else:
                        # Any other status code is an error
                        self.logger.error(f"Failed to fetch past paper, status code: {response.status}")
                        text_response = f"Failed to fetch the past paper. Status code: {response.status}"
                        failed = True
            except Exception as e:
                self.logger.error(f"Error fetching past paper: {e.__class__.__name__}")
                text_response = f"An error occurred while fetching the past paper: {str(e)}"
                failed = True
        if failed:
            await msg.edit(content=text_response)
        elif paper_file is None:
            await interaction.followup.send(content=text_response, ephemeral=False)
        else:
            view = View()
            view.add_item(GetMSfromQP(subj, year, season, paper_id))
            await interaction.followup.send(content=text_response, ephemeral=False, file=paper_file, view=view)
        return self.logger.info(f"Finished request for {interaction.user} with {subject} {year} {season} {paper_id} (Result: {'Success' if paper_file else 'Failed'})")
    @command(name="ms", description="Get a mark scheme of a specific paper.")
    @choices(subject=[Choice(name='🔢 | Further Mathematics 9231', value='further_math'), 
                      Choice(name='🧮 | Mathematics 9709', value='math'),
                      Choice(name='🧪 | Chemistry 9701', value='chemistry'),
                      Choice(name='🔬 | Physics 9702', value='physics')])
    @choices(season=[Choice(name='May/June', value='jun'), Choice(name='October/November', value='nov'), Choice(name='February/March', value='march')])
    @describe(subject="Subject you want to get the mark scheme for.",
              year="Year of the past paper (e.g. 2020)",
              season="Season of the past paper (e.g. May/June)",
              paper_id="ID of the past paper (e.g. 11)")
    async def ms(self, interaction: Interaction, subject: str, year: int, season: str, paper_id: int):
        await interaction.response.defer(ephemeral=False)
        self.logger.debug(f"Preparing to serve user {interaction.user} with mark scheme {subject} {year} {season} {paper_id}")
        subj = BestExamHelpIO().get_subject(subject)
        if not isinstance(subj, Subject):
            await interaction.followup.send("Invalid subject selected. Please try again.", ephemeral=True)
            return
        if year not in subj.years:
            await interaction.followup.send(f"Invalid year selected. Please choose a year between {subj.years.start} and {subj.years.stop - 1}.", ephemeral=True)
            return
        season = season.lower()
        season = subj.seasons.get(season)
        if not season:
            await interaction.followup.send("Invalid season selected. Please choose from May/June, October/November, or February/March.", ephemeral=True)
            return
        if paper_id not in [p for cond, pps in subj.papers for p in pps if year in cond]:
            await interaction.followup.send(f"Invalid paper ID selected for the year {year}. Please choose a valid paper ID.", ephemeral=True)
            return
        link = BestExamHelpIO().construct_link(subj, year, season, "ms", paper_id)
        msg = await interaction.followup.send("Attempting to fetch the mark scheme...", ephemeral=True)
        ms_file = None
        failed = False
        text_response = ""
        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'PastPaperBot/1.0',
                    'Accept': 'application/pdf'
                }
                self.logger.debug(f"Fetching mark scheme from {link}")
                async with session.get(link, headers=headers) as response:
                    filename = link.split('/')[-1]
                    if response.status == 304 or response.status in range(200, 300):
                        self.logger.debug(f"Successfully fetched mark scheme from {link} with status {response.status}")
                        self.logger.debug(f"Attempting to create file content for {response.url}")
                        file_content = await response.read()
                        file_bytes = BytesIO(file_content)
                        ms_file = dFile(file_bytes, filename=filename)
                        self.logger.debug(f"Mark scheme file created: {filename}, size: {len(file_content)} bytes")
                        text_response = f"Here's your mark scheme: (**{filename}**)"
            except Exception as e:
                self.logger.error(f"Error fetching mark scheme: {e.__class__.__name__}")
                text_response = f"An error occurred while fetching the mark scheme: {str(e)}"
                failed = True
        if failed:
            await msg.edit(content=text_response)
        elif ms_file is None:
            await interaction.followup.send(content=text_response, ephemeral=False)
        else:
            await interaction.followup.send(content=text_response, ephemeral=False, file=ms_file)
        return self.logger.info(f"Finished request for {interaction.user} with {subject} {year} {season} {paper_id} (Result: {'Success' if ms_file else 'Failed'})")
async def setup(bot: PPBdpy):
    # Register the dynamic button for persistence between restarts
    bot.add_dynamic_items(GetMSfromQP)
    # Add the cog
    await bot.add_cog(PaperUtils(bot))