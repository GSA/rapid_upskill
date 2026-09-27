A worker that checkpoints its own progress before each batch survives a
restart without redoing finished work [atomic-checkpoint]. A retrying
call backs off with jitter rather than retrying immediately, so a wave
of failures does not retry in lockstep [backoff-jitter]. Outbound calls
to one shared service are capped by a token bucket, so a burst of work
never exceeds what the service allows [token-bucket]. A worker also
drains its own current unit of work before exiting on a shutdown
signal [drain-on-shutdown].
