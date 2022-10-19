# ChangeLog

**NOTE: we don't aim at maintaining retro-compatibility with the original package, this may contain some breaking changes.**

## v1.0.0

_this is the first version of Mindee's fork of fastapi-cache_ <br/>
_all the changes listed here are to be taken from [this commit](https://github.com/long2ice/fastapi-cache/commit/1ef80ff457ad7524a2c2ac54e7d4ee7d473a0902) on the original repository._

### New

* :sparkles: add support for redis-sentinel (RedisSentinelBackend)

### Fixes

* :bug: ensure_async_func | add default value to .pop
* :bug: FastAPICache.clear | do not hardcode namespace if a key is provided