from mopidy.backends.base import PlaybackController
from mopidy.frontends.mpd.protocol import handle_pattern
from mopidy.frontends.mpd.exceptions import MpdNotImplemented

@handle_pattern(r'^clearerror$')
def clearerror(context):
    """
    *musicpd.org, status section:*

        ``clearerror``

        Clears the current error message in status (this is also
        accomplished by any command that starts playback).
    """
    raise MpdNotImplemented # TODO

@handle_pattern(r'^currentsong$')
def currentsong(context):
    """
    *musicpd.org, status section:*

        ``currentsong``

        Displays the song info of the current song (same song that is
        identified in status).
    """
    current_cp_track = context.backend.playback.current_cp_track.get()
    if current_cp_track is not None:
        return current_cp_track[1].mpd_format(
            position=context.backend.playback.current_playlist_position.get(),
            cpid=current_cp_track[0])

@handle_pattern(r'^idle$')
@handle_pattern(r'^idle (?P<subsystems>.+)$')
def idle(context, subsystems=None):
    """
    *musicpd.org, status section:*

        ``idle [SUBSYSTEMS...]``

        Waits until there is a noteworthy change in one or more of MPD's
        subsystems. As soon as there is one, it lists all changed systems
        in a line in the format ``changed: SUBSYSTEM``, where ``SUBSYSTEM``
        is one of the following:

        - ``database``: the song database has been modified after update.
        - ``update``: a database update has started or finished. If the
          database was modified during the update, the database event is
          also emitted.
        - ``stored_playlist``: a stored playlist has been modified,
          renamed, created or deleted
        - ``playlist``: the current playlist has been modified
        - ``player``: the player has been started, stopped or seeked
        - ``mixer``: the volume has been changed
        - ``output``: an audio output has been enabled or disabled
        - ``options``: options like repeat, random, crossfade, replay gain

        While a client is waiting for idle results, the server disables
        timeouts, allowing a client to wait for events as long as MPD runs.
        The idle command can be canceled by sending the command ``noidle``
        (no other commands are allowed). MPD will then leave idle mode and
        print results immediately; might be empty at this time.

        If the optional ``SUBSYSTEMS`` argument is used, MPD will only send
        notifications when something changed in one of the specified
        subsystems.
    """
    pass # TODO

@handle_pattern(r'^noidle$')
def noidle(context):
    """See :meth:`_status_idle`."""
    pass # TODO

@handle_pattern(r'^stats$')
def stats(context):
    """
    *musicpd.org, status section:*

        ``stats``

        Displays statistics.

        - ``artists``: number of artists
        - ``songs``: number of albums
        - ``uptime``: daemon uptime in seconds
        - ``db_playtime``: sum of all song times in the db
        - ``db_update``: last db update in UNIX time
        - ``playtime``: time length of music played
    """
    return {
        'artists': 0, # TODO
        'albums': 0, # TODO
        'songs': 0, # TODO
        'uptime': 0, # TODO
        'db_playtime': 0, # TODO
        'db_update': 0, # TODO
        'playtime': 0, # TODO
    }

@handle_pattern(r'^status$')
def status(context):
    """
    *musicpd.org, status section:*

        ``status``

        Reports the current status of the player and the volume level.

        - ``volume``: 0-100
        - ``repeat``: 0 or 1
        - ``single``: 0 or 1
        - ``consume``: 0 or 1
        - ``playlist``: 31-bit unsigned integer, the playlist version
          number
        - ``playlistlength``: integer, the length of the playlist
        - ``state``: play, stop, or pause
        - ``song``: playlist song number of the current song stopped on or
          playing
        - ``songid``: playlist songid of the current song stopped on or
          playing
        - ``nextsong``: playlist song number of the next song to be played
        - ``nextsongid``: playlist songid of the next song to be played
        - ``time``: total time elapsed (of current playing/paused song)
        - ``elapsed``: Total time elapsed within the current song, but with
          higher resolution.
        - ``bitrate``: instantaneous bitrate in kbps
        - ``xfade``: crossfade in seconds
        - ``audio``: sampleRate``:bits``:channels
        - ``updatings_db``: job id
        - ``error``: if there is an error, returns message here
    """
    result = [
        ('volume', _status_volume(context)),
        ('repeat', _status_repeat(context)),
        ('random', _status_random(context)),
        ('single', _status_single(context)),
        ('consume', _status_consume(context)),
        ('playlist', _status_playlist_version(context)),
        ('playlistlength', _status_playlist_length(context)),
        ('xfade', _status_xfade(context)),
        ('state', _status_state(context)),
    ]
    if context.backend.playback.current_track.get() is not None:
        result.append(('song', _status_songpos(context)))
        result.append(('songid', _status_songid(context)))
    if context.backend.playback.state.get() in (PlaybackController.PLAYING,
            PlaybackController.PAUSED):
        result.append(('time', _status_time(context)))
        result.append(('elapsed', _status_time_elapsed(context)))
        result.append(('bitrate', _status_bitrate(context)))
    return result

def _status_bitrate(context):
    current_track = context.backend.playback.current_track.get()
    if current_track is not None:
        return current_track.bitrate

def _status_consume(context):
    if context.backend.playback.consume.get():
        return 1
    else:
        return 0

def _status_playlist_length(context):
    return len(context.backend.current_playlist.tracks.get())

def _status_playlist_version(context):
    return context.backend.current_playlist.version.get()

def _status_random(context):
    return int(context.backend.playback.random.get())

def _status_repeat(context):
    return int(context.backend.playback.repeat.get())

def _status_single(context):
    return int(context.backend.playback.single.get())

def _status_songid(context):
    current_cpid = context.backend.playback.current_cpid.get()
    if current_cpid is not None:
        return current_cpid
    else:
        return _status_songpos(context)

def _status_songpos(context):
    return context.backend.playback.current_playlist_position.get()

def _status_state(context):
    state = context.backend.playback.state.get()
    if state == PlaybackController.PLAYING:
        return u'play'
    elif state == PlaybackController.STOPPED:
        return u'stop'
    elif state == PlaybackController.PAUSED:
        return u'pause'

def _status_time(context):
    return u'%s:%s' % (_status_time_elapsed(context) // 1000,
        _status_time_total(context) // 1000)

def _status_time_elapsed(context):
    return context.backend.playback.time_position.get()

def _status_time_total(context):
    current_track = context.backend.playback.current_track.get()
    if current_track is None:
        return 0
    elif current_track.length is None:
        return 0
    else:
        return current_track.length

def _status_volume(context):
    volume = context.mixer.volume.get()
    if volume is not None:
        return volume
    else:
        return 0

def _status_xfade(context):
    return 0 # TODO
