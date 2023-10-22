from __future__ import annotations

from typing import Iterator, Any, Dict, List, cast

from .. import models
from ..formats import NDJSON, NDJSON_LIST, PGN
from .base import FmtClient


class Tournaments(FmtClient):
    """Client for tournament-related endpoints."""

    def get(self) -> models.CurrentTournaments:
        """Get recently finished, ongoing, and upcoming tournaments.

        :return: current tournaments
        """
        path = "/api/tournament"
        return cast(
            models.CurrentTournaments,
            self._r.get(path, converter=models.Tournament.convert_values),
        )

    def get_tournament_arena(self, tournament_id: str, page: int = 1):
        """Get information about an Arena tournament.

        :param tournament_id: tournament ID
        :param page: the page number of the player standings to view
        :return: tournament information
        """
        path = f"/api/tournament/{tournament_id}?page={page}"
        return self._r.get(path, converter=models.Tournament.convert)

    def get_tournament_swiss(self, tournament_id: str):
        """Get information about a tournament.

        :param tournament_id: tournament ID
        :return: tournament information
        """
        path = f"/api/swiss/{tournament_id}"
        return self._r.get(path, converter=models.Tournament.convert)

    def join_arena(
        self,
        tournament_id: str,
        password: str | None = None,
        team: str | None = None,
        should_pair_immediately: bool = False,
    ) -> None:
        """Join an Arena tournament. Also, unpauses if you had previously paused the tournament.

        Requires OAuth2 authorization with tournament:write scope.

        :param tournament_id: tournament ID
        :param password: tournament password or user-specific entry code generated and shared by the organizer
        :param team: team with which to join the team battle Arena tournament
        :param should_pair_immediately: if the tournament is started, attempt to pair the user, even if they are not
            connected to the tournament page. This expires after one minute, to avoid pairing a user who is long gone.
            You may call "join" again to extend the waiting.
        """
        path = f"/api/tournament/{tournament_id}/join"
        params = {
            "password": password,
            "team": team,
            "pairMeAsap": should_pair_immediately,
        }
        self._r.post(path=path, params=params, converter=models.Tournament.convert)

    def join_swiss(
        self,
        tournament_id: str,
        password: str | None = None,
    ):
        """Join a tournament.

        :param tournament_id: tournament ID
        :param password: tournament password
        :return: tournament information
        """
        path = f"/api/swiss/{tournament_id}/join"
        payload = {"password": password}
        return self._r.post(
            path=path, payload=payload, converter=models.Tournament.convert
        )

    def get_team_standings(self, tournament_id: str) -> Dict[str, Any]:
        """Get team standing of a team battle tournament, with their respective top players.

        :param tournament_id: tournament ID
        :return: information about teams in the team battle tournament
        """
        path = f"/api/tournament/{tournament_id}/teams"
        return self._r.get(path)

    def update_team_battle(
        self,
        tournament_id: str,
        team_ids: str | None = None,
        team_leader_count_per_team: int | None = None,
    ) -> Dict[str, Any]:
        """Set the teams and number of leaders of a team battle tournament.

        :param tournament_id: tournament ID
        :param team_ids: all team IDs of the team battle, separated by commas
        :param team_leader_count_per_team: number of team leaders per team
        :return: updated team battle information
        """
        path = f"/api/tournament/team-battle/{tournament_id}"
        params = {"teams": team_ids, "nbLeaders": team_leader_count_per_team}
        return self._r.post(path=path, params=params)

    def create_arena(
        self,
        clockTime: int,
        clockIncrement: int,
        minutes: int,
        name: str | None = None,
        wait_minutes: int | None = None,
        startDate: int | None = None,
        variant: str | None = None,
        rated: bool | None = None,
        position: str | None = None,
        berserkable: bool | None = None,
        streakable: bool | None = None,
        hasChat: bool | None = None,
        description: str | None = None,
        password: str | None = None,
        teamBattleByTeam: str | None = None,
        teamId: str | None = None,
        minRating: int | None = None,
        maxRating: int | None = None,
        nbRatedGame: int | None = None,
    ) -> Dict[str, Any]:
        """Create a new arena tournament.

        .. note::

            ``wait_minutes`` is always relative to now and is overridden by
            ``start_time``.

        .. note::

            If ``name`` is left blank then one is automatically created.

        :param clockTime: initial clock time in minutes
        :param clockIncrement: clock increment in seconds
        :param minutes: length of the tournament in minutes
        :param name: tournament name
        :param wait_minutes: future start time in minutes
        :param startDate: when to start the tournament (timestamp in milliseconds)
        :param variant: variant to use if other than standard
        :param rated: whether the game affects player ratings
        :param position: custom initial position in FEN
        :param berserkable: whether players can use berserk
        :param streakable: whether players get streaks
        :param hasChat: whether players can discuss in a chat
        :param description: anything you want to tell players about the tournament
        :param password: password
        :param teamBattleByTeam: ID of a team you lead to create a team battle
        :param teamId: Restrict entry to members of team
        :param minRating: Minimum rating to join
        :param maxRating: Maximum rating to join
        :param nbRatedGame: Min number of rated games required
        :return: created tournament info
        """
        path = "/api/tournament"
        payload = {
            "name": name,
            "clockTime": clockTime,
            "clockIncrement": clockIncrement,
            "minutes": minutes,
            "waitMinutes": wait_minutes,
            "startDate": startDate,
            "variant": variant,
            "rated": rated,
            "position": position,
            "berserkable": berserkable,
            "streakable": streakable,
            "hasChat": hasChat,
            "description": description,
            "password": password,
            "teamBattleByTeam": teamBattleByTeam,
            "conditions.teamMember.teamId": teamId,
            "conditions.minRating.rating": minRating,
            "conditions.maxRating.rating": maxRating,
            "conditions.nbRatedGame.nb": nbRatedGame,
        }
        return self._r.post(path, json=payload, converter=models.Tournament.convert)

    def create_swiss(
        self,
        teamId: str,
        clockLimit: int,
        clockIncrement: int,
        nbRounds: int,
        name: str | None = None,
        startsAt: int | None = None,
        roundInterval: int | None = None,
        variant: str | None = None,
        description: str | None = None,
        rated: bool | None = None,
        chatFor: int | None = None,
    ) -> Dict[str, Any]:
        """Create a new swiss tournament.

        .. note::

            If ``name`` is left blank then one is automatically created.

        .. note::

            If ``startsAt`` is left blank then the tournament begins 10 minutes after
            creation

        :param teamId: team ID, required for swiss tournaments
        :param clockLimit: initial clock time in seconds
        :param clockIncrement: clock increment in seconds
        :param nbRounds: maximum number of rounds to play
        :param name: tournament name
        :param startsAt: when to start tournament (timestamp in milliseconds)
        :param roundInterval: interval between rounds in seconds
        :param variant: variant to use if other than standard
        :param description: tournament description
        :param rated: whether the game affects player ratings
        :param chatFor: who can read and write in the chat
        :return: created tournament info
        """
        path = f"/api/swiss/new/{teamId}"

        payload = {
            "name": name,
            "clock.limit": clockLimit,
            "clock.increment": clockIncrement,
            "nbRounds": nbRounds,
            "startsAt": startsAt,
            "roundInterval": roundInterval,
            "variant": variant,
            "description": description,
            "rated": rated,
            "chatFor": chatFor,
        }
        return self._r.post(path, json=payload, converter=models.Tournament.convert)

    def export_arena_games(
        self,
        id: str,
        as_pgn: bool | None = None,
        moves: bool = True,
        tags: bool = True,
        clocks: bool = False,
        evals: bool = True,
        opening: bool = False,
    ) -> Iterator[str] | Iterator[Dict[str, Any]]:
        """Export games from an arena tournament.

        :param id: tournament ID
        :param as_pgn: whether to return PGN instead of JSON
        :param moves: include moves
        :param tags: include tags
        :param clocks: include clock comments in the PGN moves, when available
        :param evals: include analysis evaluation comments in the PGN moves, when
            available
        :param opening: include the opening name
        :return: iterator over the exported games, as JSON or PGN
        """
        path = f"/api/tournament/{id}/games"
        params = {
            "moves": moves,
            "tags": tags,
            "clocks": clocks,
            "evals": evals,
            "opening": opening,
        }
        if self._use_pgn(as_pgn):
            yield from self._r.get(path, params=params, fmt=PGN, stream=True)
        else:
            yield from self._r.get(
                path,
                params=params,
                fmt=NDJSON,
                stream=True,
                converter=models.Game.convert,
            )

    def export_swiss_games(
        self,
        id: str,
        as_pgn: bool | None = None,
        moves: bool = True,
        pgnInJson: bool = False,
        tags: bool = True,
        clocks: bool = False,
        evals: bool = True,
        opening: bool = False,
    ) -> Iterator[str] | Iterator[Dict[str, Any]]:
        """Export games from a swiss tournament.

        :param id: tournament id
        :param as_pgn: whether to return pgn instead of JSON
        :param moves: include moves
        :param pgnInJson: include the full PGN within the JSON response, in a pgn field
        :param tags: include tags
        :param clocks: include clock comments
        :param evals: include analysis evaluation comments in the PGN, when available
        :param opening: include the opening name
        :return: iterator over the exported games, as JSON or PGN
        """
        path = f"/api/swiss/{id}/games"
        params = {
            "moves:": moves,
            "pgnInJson": pgnInJson,
            "tags": tags,
            "clocks": clocks,
            "evals": evals,
            "opening": opening,
        }
        if self._use_pgn(as_pgn):
            yield from self._r.get(path, params=params, fmt=PGN, stream=True)
        else:
            yield from self._r.get(
                path,
                params=params,
                fmt=NDJSON,
                stream=True,
                converter=models.Game.convert,
            )

    def export_trf(self, tournament_id: str):
        """Download a tournament in the Tournament Report File format, the FIDE standard.

        :param tournament_id: tournament ID
        :return: TRF representation of tournament
        """
        path = f"/swiss/{tournament_id}/.trf"
        return self._r.get(path)

    def tournaments_by_user(
        self, username: str, nb: int | None = None
    ) -> List[Dict[str, Any]]:
        """Get tournaments created by a user.

        :param username: username
        :param nb: max number of tournaments to fetch
        :return: tournaments
        """

        path = f"/api/user/{username}/tournament/created"
        params = {
            "nb": nb,
        }
        return self._r.get(
            path, params=params, fmt=NDJSON_LIST, converter=models.Game.convert
        )

    def arenas_by_team(
        self, teamId: str, maxT: int | None = None
    ) -> List[Dict[str, Any]]:
        """Get arenas created for a team.

        :param teamId: team ID
        :param maxT: how many tournaments to download
        :return: tournaments
        """
        path = f"/api/team/{teamId}/arena"
        params = {
            "max": maxT,
        }
        return self._r.get(
            path, params=params, fmt=NDJSON_LIST, converter=models.Game.convert
        )

    def swiss_by_team(
        self, teamId: str, maxT: int | None = None
    ) -> List[Dict[str, Any]]:
        """Get swiss tournaments created for a team.

        :param teamId: team ID
        :param maxT: how many tournaments to download
        :return: tournaments
        """
        path = f"/api/team/{teamId}/swiss"
        params = {
            "max": maxT,
        }
        return self._r.get(
            path, params=params, fmt=NDJSON_LIST, converter=models.Game.convert
        )

    def schedule_next_round(
        self, tournament_id: str, start_timestamp_milliseconds: int
    ) -> None:
        """Manually schedule the next round date and time of a Swiss tournament.

        This sets the roundInterval field to 99999999, i.e. manual scheduling.

        All further rounds will need to be manually scheduled, unless the roundInterval field is changed back to
        automatic scheduling.

        :param tournament_id: tournament ID
        :param start_timestamp_milliseconds: timestamp in milliseconds to start the next round at a given date and time
        """
        path = f"/api/swiss/{tournament_id}/schedule-next-round"
        payload = {"date": start_timestamp_milliseconds}
        return self._r.post(path=path, payload=payload)

    def stream_results_arena(
        self, tournament_id: str, limit: int | None = None
    ) -> Iterator[Dict[str, Any]]:
        """Stream the results of a tournament.

        Results are the players of a tournament with their scores and performance in
        rank order. Note that results for ongoing tournaments can be inconsistent due to
        ranking changes.

        :param tournament_id: tournament ID
        :param limit: maximum number of results to stream
        :return: iterator over the results
        """
        path = f"/api/tournament/{tournament_id}/results"
        params = {"nb": limit}
        yield from self._r.get(path, params=params, stream=True)

    def stream_results_swiss(
        self, tournament_id: str, limit: int | None = None
    ) -> Iterator[Dict[str, Any]]:
        """Stream the results of a tournament.

        Results are the players of a tournament with their scores and performance in
        rank order. Note that results for ongoing tournaments can be inconsistent due to
        ranking changes.

        :param tournament_id: tournament ID
        :param limit: maximum number of results to stream
        :return: iterator over the results
        """
        path = f"/api/swiss/{tournament_id}/results"
        params = {"nb": limit}
        yield from self._r.get(path, params=params, stream=True)

    def stream_by_creator(self, username: str) -> Iterator[Dict[str, Any]]:
        """Stream the tournaments created by a player.

        :param username: username of the player
        :return: iterator over the tournaments
        """
        path = f"/api/user/{username}/tournament/created"
        yield from self._r.get(path, stream=True)

    def terminate_arena(self, tournament_id: str) -> None:
        """Terminate an Arena tournament.

        :param tournament_id: tournament ID
        """
        path = f"/api/tournament/{tournament_id}/terminate"
        self._r.post(path)

    def terminate_swiss(self, tournament_id: str) -> None:
        """Terminate a tournament.

        :param tournament_id: tournament ID
        """
        path = f"/api/swiss/{tournament_id}/terminate"
        self._r.post(path)

    def update_arena(
        self,
        tournament_id: str,
        initial_clock_time_minutes: float,
        increment_clock_time_seconds: int,
        duration_minutes: int,
        name: str | None = None,
        wait_minutes: int | None = None,
        start_timestamp_milliseconds: int | None = None,
        variant: str | None = None,
        rated: bool = True,
        position: str | None = None,
        berserkable: bool = True,
        streakable: bool = True,
        has_chat: bool = True,
        description: str | None = None,
        password: str | None = None,
        min_rating: int | None = None,
        max_rating: int | None = None,
        min_rated_games_count: int | None = None,
        allowed_usernames: str | None = None,
    ) -> Dict[str, Any]:
        """Updates a tournament.

        Be mindful not to make important changes to ongoing tournaments. Can be used to update a team battle.

        .. note::

            ``wait_minutes`` is always relative to now and is overridden by
            ``start_time``.

        .. note::

            If ``name`` is left blank then one is automatically created.

        :param tournament_id: tournament ID
        :param initial_clock_time_minutes: initial clock time in minutes
        :param increment_clock_time_seconds: clock increment in seconds
        :param duration_minutes: length of the tournament in minutes
        :param name: tournament name
        :param wait_minutes: future start time in minutes
        :param start_timestamp_milliseconds: when to start the tournament (timestamp in milliseconds)
        :param variant: variant to use if other than standard
        :param rated: whether the game affects player ratings
        :param position: custom initial position in FEN
        :param berserkable: whether players can use berserk
        :param streakable: whether players get streaks
        :param has_chat: whether players can discuss in a chat
        :param description: anything you want to tell players about the tournament
        :param password: password
        :param min_rating: minimum rating to join
        :param max_rating: maximum rating to join
        :param min_rated_games_count: min number of rated games required
        :param allowed_usernames: predefined usernames that are allowed to join, separated by commas
        :return: created tournament info
        """
        path = f"/api/tournament/{tournament_id}"
        payload = {
            "name": name,
            "clockTime": initial_clock_time_minutes,
            "clockIncrement": increment_clock_time_seconds,
            "minutes": duration_minutes,
            "waitMinutes": wait_minutes,
            "startDate": start_timestamp_milliseconds,
            "variant": variant,
            "rated": rated,
            "position": position,
            "berserkable": berserkable,
            "streakable": streakable,
            "hasChat": has_chat,
            "description": description,
            "password": password,
            "conditions.minRating.rating": min_rating,
            "conditions.maxRating.rating": max_rating,
            "conditions.nbRatedGame.nb": min_rated_games_count,
            "conditions.allowList": allowed_usernames,
        }
        return self._r.post(path, json=payload, converter=models.Tournament.convert)

    def update_swiss(
        self,
        tournament_id: str,
        initial_clock_time_minutes: float,
        increment_clock_time_seconds: int,
        max_rounds: int,
        name: str | None = None,
        start_timestamp_milliseconds: int | None = None,
        round_interval: int | None = None,
        variant: str | None = None,
        description: str | None = None,
        rated: bool = True,
        password: str | None = None,
        forbidden_pairings: str | None = None,
        manual_pairings: str | None = None,
        chat_read_write_permissions: int | None = None,
        min_rating: int | None = None,
        max_rating: int | None = None,
        min_rated_games_count: int | None = None,
        allowed_usernames: str | None = None,
    ) -> Dict[str, Any]:
        """Updates a tournament.

        Be mindful not to make important changes to ongoing tournaments.

        .. note::

            For chat_read_write_permissions, 0 = No one, 10 = Only team leaders, 20 = Only team members, 30 = All players

        .. note::

            If ``name`` is left blank then one is automatically created.

        :param tournament_id: tournament ID
        :param initial_clock_time_minutes: initial clock time in minutes
        :param increment_clock_time_seconds: clock increment in seconds
        :param max_rounds: maximum number of rounds to play
        :param name: tournament name
        :param start_timestamp_milliseconds: when to start the tournament (timestamp in milliseconds)
        :param round_interval: number of seconds to wait between each round
        :param variant: variant to use if other than standard
        :param description: anything you want to tell players about the tournament
        :param rated: whether the game affects player ratings
        :param password: password
        :param forbidden_pairings: usernames of players that must not play together, two per line, separated by a space
        :param manual_pairings: manual pairings for the next round, two usernames per line, separated by a space
        :param chat_read_write_permissions: who can read and write in the chat
        :param min_rating: minimum rating to join
        :param max_rating: maximum rating to join
        :param min_rated_games_count: min number of rated games required
        :param allowed_usernames: predefined usernames that are allowed to join, separated by commas
        :return: created tournament info
        """
        path = f"/api/swiss/{tournament_id}/edit"
        payload = {
            "name": name,
            "clock.limit": initial_clock_time_minutes,
            "clock.increment": increment_clock_time_seconds,
            "nbRounds": max_rounds,
            "startDate": start_timestamp_milliseconds,
            "roundInterval": round_interval,
            "variant": variant,
            "description": description,
            "rated": rated,
            "password": password,
            "forbiddenPairings": forbidden_pairings,
            "manualPairings": manual_pairings,
            "chatFor": chat_read_write_permissions,
            "conditions.minRating.rating": min_rating,
            "conditions.maxRating.rating": max_rating,
            "conditions.nbRatedGame.nb": min_rated_games_count,
            "conditions.allowList": allowed_usernames,
        }
        return self._r.post(path, json=payload, converter=models.Tournament.convert)

    def withdraw_arena(self, tournament_id: str) -> None:
        """Leave an upcoming Arena tournament, or take a break on an ongoing Arena tournament.

        :param tournament_id: tournament ID
        """
        path = f"/api/tournament/{tournament_id}/withdraw"
        self._r.post(path)

    def withdraw_swiss(self, tournament_id: str) -> None:
        """Leave an upcoming tournament, or take a break on an ongoing tournament.

        :param tournament_id: tournament ID
        """
        path = f"/api/swiss/{tournament_id}/withdraw"
        self._r.post(path)
