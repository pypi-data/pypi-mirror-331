from pyespn.core import *
from pyespn.data.leagues import LEAGUE_API_MAPPING
from pyespn.data.teams import LEAGUE_TEAMS_MAPPING
from pyespn.data.betting import BETTING_PROVIDERS


class PYESPN():
    LEAGUE_API_MAPPING = LEAGUE_API_MAPPING
    valid_leagues = {league['league_abbv'] for league in LEAGUE_API_MAPPING}

    def __init__(self, sport_league='nfl'):
        # Validate sport_league
        if sport_league not in self.valid_leagues:
            raise ValueError(f"Invalid sport league: '{sport_league}'. Must be one of {self.valid_leagues}")

        self.league_abbv = sport_league
        self.TEAM_ID_MAPPING = LEAGUE_TEAMS_MAPPING[self.league_abbv]
        self.BETTING_PROVIDERS = BETTING_PROVIDERS

    def get_player_info(self, player_id):
        return get_player_info_core(player_id=player_id,
                                    league_abbv=self.league_abbv)

    def get_player_ids(self):
        return get_player_ids_core(league_abbv=self.league_abbv)

    def get_recruiting_rankings(self, season, max_pages=None):
        return get_recruiting_rankings_core(season=season,
                                            league_abbv=self.league_abbv,
                                            max_pages=max_pages)

    def get_game_info(self, event_id):
        return get_game_info_core(event_id=event_id,
                                  league_abbv=self.league_abbv)

    def get_team_info(self, team_id):
        return get_team_info_core(team_id=team_id,
                                  league_abbv=self.league_abbv)

    def get_season_team_stats(self, season):
        return get_season_team_stats_core(season=season,
                                          league_abbv=self.league_abbv)

    def get_draft_pick_data(self, season, pick_round, pick):
        return get_draft_pick_data_core(season=season,
                                        pick_round=pick_round,
                                        pick=pick,
                                        league_abbv=self.league_abbv)

    def get_players_historical_stats(self, player_id):
        return get_players_historical_stats_core(player_id=player_id,
                                                 league_abbv=self.league_abbv)

    def get_league_year_champion_futures(self, season, provider='DraftKings'):
        return get_year_league_champions_futures_core(season=season,
                                                      league_abbv=self.league_abbv,
                                                      provider=provider)

    def get_league_year_division_champs_futures(self, season, division, provider='DraftKings'):
        return get_division_champ_futures_core(season=season,
                                               division=division,
                                               league_abbv=self.league_abbv,
                                               provider=provider)

    def get_team_year_ats_away(self, team_id, season):
        return get_team_year_ats_away_core(team_id=team_id,
                                           season=season,
                                           league_abbv=self.league_abbv)

    def get_team_year_ats_home_favorite(self, team_id, season):
        return get_team_year_ats_home_favorite_core(team_id=team_id,
                                                    season=season,
                                                    league_abbv=self.league_abbv)

    def get_team_year_ats_away_underdog(self, team_id, season):
        return get_team_year_ats_away_underdog_core(team_id=team_id,
                                                    season=season,
                                                    league_abbv=self.league_abbv)

    def get_team_year_ats_favorite(self, team_id, season):
        return get_team_year_ats_favorite_core(team_id=team_id,
                                               season=season,
                                               league_abbv=self.league_abbv)

    def get_team_year_ats_home(self, team_id, season):
        return get_team_year_ats_home_core(team_id=team_id,
                                           season=season,
                                           league_abbv=self.league_abbv)

    def get_team_year_ats_overall(self, team_id, season):
        return get_team_year_ats_overall_core(team_id=team_id,
                                              season=season,
                                              league_abbv=self.league_abbv)

    def get_team_year_ats_underdog(self, team_id, season):
        return get_team_year_ats_underdog_core(team_id=team_id,
                                               season=season,
                                               league_abbv=self.league_abbv)

    def get_team_year_ats_home_underdog(self, team_id, season):
        return get_team_year_ats_home_underdog_core(team_id=team_id,
                                                    season=season,
                                                    league_abbv=self.league_abbv)

