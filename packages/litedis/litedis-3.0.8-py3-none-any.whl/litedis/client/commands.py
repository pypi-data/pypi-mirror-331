from typing import Any, Protocol, Tuple, Dict, List


class ClientCommands(Protocol):

    def execute(self, *args) -> Any: ...


class BasicCommands(ClientCommands):
    """
    BasicCommands class provides basic database operation commands
    """

    def append(self, key: str, value: str) -> int:
        """
        Append a value to the end of the string stored at the key.

        If key already exists and is a string, this command appends the value at the end of the string.
        If key does not exist it is created and set as an empty string, so APPEND will be similar to SET in this special case.

        Args:
            key (str): The key of the value to be appended.
            value (str): The value to be appended.

        Returns:
            int: Returns the length of the string after the append operation.
        """
        return self.execute("append", key, value)

    def copy(self, source: str, destination: str, replace: bool = False) -> int:
        """
        Copy the value from the source key to the destination key.

        Args:
            source (str): The source key.
            destination (str): The destination key.
            replace (bool): Whether to replace the destination key if it already exists, default is False.

        Returns:
            int: Returns 1 if source was copied. Returns 0 if source was not copied.
        """
        pieces = [source, destination]
        if replace:
            pieces.append("replace")
        return self.execute("copy", *pieces)

    def decrby(self, key: str, decrement: int) -> int:
        """
        Decrease the integer value of the key by the specified decrement.

        Args:
            key (str): The key of the value to be decreased.
            decrement (int): The decrement value.

        Returns:
            int: Returns the value of the key after decrementing it.
        """
        result = self.execute("decrby", key, str(decrement))
        return int(result)

    def delete(self, *keys: str) -> int:
        """
        Deletes the specified keys. A key is ignored if it does not exist.

        Args:
            *keys (str): One or more keys to be deleted.

        Returns:
            int: Returns the number of keys that were deleted.
        """
        return self.execute("del", *keys)

    def exists(self, *keys: str) -> int:
        """
        Check if one or more keys exist.

        Args:
            *keys (str): One or more keys to be checked.

        Returns:
            int: Returns the number of keys that exist from those specified as arguments.
        """
        return self.execute("exists", *keys)

    def expire(
            self,
            key: str,
            seconds: int,
            nx: bool = False,  # Set expiry only when the key has no expiry
            xx: bool = False,  # Set expiry only when the key has an existing expiry
            gt: bool = False,  # Set expiry only when the new expiry is greater than current one
            lt: bool = False,  # Set expiry only when the new expiry is less than current one
    ) -> int:
        """
        Set an expiration time (in seconds) for the key.

        Args:
            key (str): The key to set the expiration time.
            seconds (int): The expiration time in seconds.
            nx (bool): Set expiry only when the key has no expiry, default is False.
            xx (bool): Set expiry only when the key has an existing expiry, default is False.
            gt (bool): Set expiry only when the new expiry is greater than current one, default is False.
            lt (bool): Set expiry only when the new expiry is less than current one, default is False.

        Returns:
            int: Returns 0 if the timeout was not set. Returns 1 if the timeout was set.
        """
        pieces = [key, str(seconds)]
        if nx:
            pieces.append("NX")
        if xx:
            pieces.append("XX")
        if gt:
            pieces.append("GT")
        if lt:
            pieces.append("LT")
        return self.execute("expire", *pieces)

    def expireat(
            self,
            key: str,
            timestamp: int,
            nx: bool = False,  # Set expiry only when the key has no expiry
            xx: bool = False,  # Set expiry only when the key has an existing expiry
            gt: bool = False,  # Set expiry only when the new expiry is greater than current one
            lt: bool = False,  # Set expiry only when the new expiry is less than current one
    ) -> int:
        """
        Set an expiration time (in timestamp) for the key.

        Args:
            key (str): The key to set the expiration time.
            timestamp (int): The expiration timestamp.
            nx (bool): Set expiry only when the key has no expiry, default is False.
            xx (bool): Set expiry only when the key has an existing expiry, default is False.
            gt (bool): Set expiry only when the new expiry is greater than current one, default is False.
            lt (bool): Set expiry only when the new expiry is less than current one, default is False.

        Returns:
            int: Returns 0 if the timeout was not set. Returns 1 if the timeout was set.
        """
        pieces = [key, str(timestamp)]
        if nx:
            pieces.append("NX")
        if xx:
            pieces.append("XX")
        if gt:
            pieces.append("GT")
        if lt:
            pieces.append("LT")
        return self.execute("expireat", *pieces)

    def expiretime(self, key: str) -> int:
        """
        Returns the absolute Unix timestamp (since January 1, 1970) in seconds at which the given key will expire.

        Args:
            key (str): The key to get the expiration time.

        Returns:
            int: Returns the expiration Unix timestamp in seconds.
            Returns -1 if the key exists but has no associated expiration time.
            Returns -2 if the key does not exist.
        """
        return self.execute("expiretime", key)

    def get(self, key: str) -> Any:
        """
        Get the value of the key.

        Args:
            key (str): The key to get the value.

        Returns:
            Any: Returns the value of the key. Returns None if the key does not exist.
        """
        return self.execute("get", key)

    def set(
            self,
            key: str,
            value: str,
            ex: int = None,
            px: int = None,
            nx: bool = False,
            xx: bool = False,
            keepttl: bool = False,
            get: bool = False,
            exat: int = None,
            pxat: int = None,
    ) -> Any:
        """
        Set the value of the key.

        Args:
            key (str): The key to set the value.
            value (str): The value to be set.
            ex (int): Set the expiration time in seconds, default is None.
            px (int): Set the expiration time in milliseconds, default is None.
            nx (bool): Set the key only if it does not exist, default is False.
            xx (bool): Set the key only if it already exists, default is False.
            keepttl (bool): Keep the original expiration time, default is False.
            get (bool): Return the old value, default is False.
            exat (int): Set the expiration timestamp in seconds, default is None.
            pxat (int): Set the expiration timestamp in milliseconds, default is None.

        Returns:
            Any: Returns 'OK' if 'GET' not given: The key was set.
            Returns the previous value of the key if 'GET' is given.
            Returns None if the key was not set.
        """
        pieces: list = [key, value]
        if ex is not None:
            pieces.append("ex")
            pieces.append(ex)
        if px is not None:
            pieces.append("px")
            pieces.append(px)
        if exat is not None:
            pieces.append("exat")
            pieces.append(exat)
        if pxat is not None:
            pieces.append("pxat")
            pieces.append(pxat)

        if keepttl:
            pieces.append("keepttl")

        if nx:
            pieces.append("nx")
        if xx:
            pieces.append("xx")

        if get:
            pieces.append("get")

        return self.execute("set", *pieces)

    def incrby(self, key: str, increment: int = 1) -> int:
        """
        Increase the integer value of the key by the specified increment.

        Args:
            key (str): The key of the value to be increased.
            increment (int): The increment value, default is 1.

        Returns:
            int: Returns the value of the key after the increment.
        """
        result = self.execute("incrby", key, str(increment))
        return int(result)

    def incrbyfloat(self, key: str, increment: float = 1.) -> float:
        """
        Increase the floating-point value of the key by the specified increment.

        Args:
            key (str): The key of the value to be increased.
            increment (float): The increment value, default is 1.

        Returns:
            Any: Returns the value of the key after the increment.
        """
        result = self.execute("incrbyfloat", key, str(increment))
        return float(result)

    def keys(self, pattern: str = "*") -> Any:
        """
        Get all keys matching the specified pattern.

        Args:
            pattern (str): The pattern to match keys, default is "*".
                * - matches any sequence of characters
                ? - matches any single character
                [] - matches any character within the brackets
                \\x - escape character x

        Returns:
            Any: Returns a list of keys matching pattern.
        """
        return self.execute("keys", pattern)

    def mget(self, *keys: str) -> Any:
        """
        Get the values of one or more keys.

        Args:
            *keys (str): One or more keys to get the values.

        Returns:
            Any: Returns a list of values corresponding to the keys.
        """
        return self.execute("mget", *keys)

    def mset(self, mapping: Dict[str, str]) -> str:
        """
        Set multiple keys and their values.

        Args:
            mapping (Dict[str, str]): A dictionary containing key-value pairs.

        Returns:
            str: Always returns 'OK' because MSET can't fail.
        """
        pieces: List[str] = []
        for key, value in mapping.items():
            pieces.extend([key, value])
        return self.execute("mset", *pieces)

    def msetnx(self, mapping: Dict[str, str]) -> int:
        """
        Set multiple keys and their values only if none of the keys exist.

        Args:
            mapping (Dict[str, str]): A dictionary containing key-value pairs.

        Returns:
            int: Returns 0 if no key was set. Returns 1 if all keys were set.
        """
        pieces: List[str] = []
        for key, value in mapping.items():
            pieces.extend([key, value])
        return self.execute("msetnx", *pieces)

    def persist(self, key: str) -> int:
        """
        Remove the expiration time of the key.

        Args:
            key (str): The key to remove the expiration time.

        Returns:
            int: Returns 0 if key does not exist or does not have an associated timeout.
            Returns 1 if the timeout was removed.
        """
        return self.execute("persist", key)

    def randomkey(self) -> Any:
        """
        Get a random key from the database.

        Returns:
            Any: Returns a random key in the database.
            Returns None if the database is empty.
        """
        return self.execute("randomkey")

    def rename(self, source: str, destination: str) -> str:
        """
        Rename the source key to the destination key.

        Args:
            source (str): The source key.
            destination (str): The destination key.

        Returns:
            str: Returns 'OK'
        """
        return self.execute("rename", source, destination)

    def renamenx(self, source: str, destination: str) -> int:
        """
        Rename the source key to the destination key only if the destination key does not exist.

        Args:
            source (str): The source key.
            destination (str): The destination key.

        Returns:
            int: Returns 1 if key was renamed to newkey.
            Returns 0 if newkey already exists.
        """
        return self.execute("renamenx", source, destination)

    def strlen(self, key: str) -> int:
        """
        Get the length of the string stored at the key.

        Args:
            key (str): The key to get the string length.

        Returns:
            int: Returns the length of the string stored at key, or 0 when the key does not exist.
        """
        return self.execute("strlen", key)

    def substr(self, key: str, start: int, end: int) -> str:
        """
        Get a substring of the string stored at the key.

        Args:
            key (str): The key to get the substring.
            start (int): The starting index of the substring.
            end (int): The ending index of the substring.

        Returns:
            str: Returns the substring of the string stored at key.
        """
        return self.execute("substr", key, str(start), str(end))

    def ttl(self, key: str) -> int:
        """
        Get the remaining time to live (in seconds) of the key.

        Args:
            key (str): The key to get the remaining time to live.

        Returns:
            int: Returns TTL in seconds.
            Returns -1 if the key exists but has no associated expire.
            Returns -2 if the key does not exist.
        """
        return self.execute("ttl", key)

    def type(self, key: str) -> str:
        """
        Get the data type of the key.

        Args:
            key (str): The key to get the data type.

        Returns:
            str: Returns the type of key, or 'none' when key doesn't exist.
        """
        return self.execute("type", key)


class HashCommands(ClientCommands):
    def hdel(self, key: str, *fields: str) -> Any:
        return self.execute("hdel", key, *fields)

    def hexists(self, key: str, field: str) -> Any:
        return self.execute("hexists", key, field)

    def hget(self, key: str, field: str) -> Any:
        return self.execute("hget", key, field)

    def hgetall(self, key: str) -> Any:
        return self.execute("hgetall", key)

    def hincrby(self, key: str, field: str, increment: int = 1) -> Any:
        return self.execute("hincrby", key, field, str(increment))

    def hincrbyfloat(self, key: str, field: str, increment: float = 1.) -> Any:
        return self.execute("hincrbyfloat", key, field, str(increment))

    def hkeys(self, key: str) -> Any:
        return self.execute("hkeys", key)

    def hlen(self, key: str) -> Any:
        return self.execute("hlen", key)

    def hmget(self, key: str, *fields: str) -> Any:
        return self.execute("hmget", key, *fields)

    def hset(self, key: str, mapping: Dict[str, str]) -> Any:
        pieces: List[str] = []
        for field, value in mapping.items():
            pieces.extend([field, value])
        return self.execute("hset", key, *pieces)

    def hsetnx(self, key: str, field: str, value: str) -> Any:
        return self.execute("hsetnx", key, field, value)

    def hstrlen(self, key: str, field: str) -> Any:
        return self.execute("hstrlen", key, field)

    def hvals(self, key: str) -> Any:
        return self.execute("hvals", key)

    def hscan(
            self,
            key: str,
            cursor: int = 0,
            match: str = None,
            count: int = None
    ) -> Any:
        pieces = [key, str(cursor)]
        if match is not None:
            pieces.extend(["MATCH", match])
        if count is not None:
            pieces.extend(["COUNT", str(count)])
        return self.execute("hscan", *pieces)


class ListCommands(ClientCommands):
    def lindex(self, key: str, index: int) -> Any:
        return self.execute("lindex", key, str(index))

    def linsert(self, key: str, before: bool, pivot: str, element: str) -> Any:
        position = "BEFORE" if before else "AFTER"
        return self.execute("linsert", key, position, pivot, element)

    def llen(self, key: str) -> Any:
        return self.execute("llen", key)

    def lpop(self, key: str, count: int = None) -> Any:
        pieces = [key]
        if count is not None:
            pieces.append(str(count))
        return self.execute("lpop", *pieces)

    def lpush(self, key: str, *elements: str) -> Any:
        return self.execute("lpush", key, *elements)

    def lpushx(self, key: str, *elements: str) -> Any:
        return self.execute("lpushx", key, *elements)

    def lrange(self, key: str, start: int, stop: int) -> Any:
        return self.execute("lrange", key, str(start), str(stop))

    def lrem(self, key: str, count: int, element: str) -> Any:
        return self.execute("lrem", key, str(count), element)

    def lset(self, key: str, index: int, element: str) -> Any:
        return self.execute("lset", key, str(index), element)

    def ltrim(self, key: str, start: int, stop: int) -> Any:
        return self.execute("ltrim", key, str(start), str(stop))

    def rpop(self, key: str, count: int = None) -> Any:
        pieces = [key]
        if count is not None:
            pieces.append(str(count))
        return self.execute("rpop", *pieces)

    def rpush(self, key: str, *elements: str) -> Any:
        return self.execute("rpush", key, *elements)

    def rpushx(self, key: str, *elements: str) -> Any:
        return self.execute("rpushx", key, *elements)

    def sort(
            self,
            key: str,
            desc: bool = False,
            alpha: bool = False,
            store: str = None
    ) -> Any:
        pieces = [key]
        if desc:
            pieces.append("DESC")
        if alpha:
            pieces.append("ALPHA")
        if store is not None:
            pieces.extend(["STORE", store])
        return self.execute("sort", *pieces)


class SetCommands(ClientCommands):
    def sadd(self, key: str, *members: str) -> Any:
        return self.execute("sadd", key, *members)

    def scard(self, key: str) -> Any:
        return self.execute("scard", key)

    def sdiff(self, *keys: str) -> Any:
        return self.execute("sdiff", *keys)

    def sdiffstore(self, destination: str, *keys: str) -> Any:
        return self.execute("sdiffstore", destination, *keys)

    def sinter(self, *keys: str) -> Any:
        return self.execute("sinter", *keys)

    def sintercard(
            self,
            numkeys: int,
            *keys: str,
            limit: int = None
    ) -> Any:
        pieces = [str(numkeys)]
        pieces.extend(keys)
        if limit is not None:
            pieces.extend(["LIMIT", str(limit)])
        return self.execute("sintercard", *pieces)

    def sinterstore(self, destination: str, *keys: str) -> Any:
        return self.execute("sinterstore", destination, *keys)

    def sismember(self, key: str, member: str) -> Any:
        return self.execute("sismember", key, member)

    def smembers(self, key: str) -> Any:
        return self.execute("smembers", key)

    def smismember(self, key: str, *members: str) -> Any:
        return self.execute("smismember", key, *members)

    def smove(self, source: str, destination: str, member: str) -> Any:
        return self.execute("smove", source, destination, member)

    def spop(self, key: str, count: int = None) -> Any:
        pieces = [key]
        if count is not None:
            pieces.append(str(count))
        return self.execute("spop", *pieces)

    def srandmember(self, key: str, count: int = None) -> Any:
        pieces = [key]
        if count is not None:
            pieces.append(str(count))
        return self.execute("srandmember", *pieces)

    def srem(self, key: str, *members: str) -> Any:
        return self.execute("srem", key, *members)

    def sunion(self, *keys: str) -> Any:
        return self.execute("sunion", *keys)


class ZSetCommands(ClientCommands):
    def zadd(self, key: str, mapping: Dict[str, float]) -> Any:
        pieces: List[str] = []
        for member, score in mapping.items():
            pieces.extend([str(score), member])
        return self.execute("zadd", key, *pieces)

    def zcard(self, key: str) -> Any:
        return self.execute("zcard", key)

    def zcount(self, key: str, min_score: float, max_score: float) -> Any:
        return self.execute("zcount", key, str(min_score), str(max_score))

    def zdiff(self, *keys: str, withscores: bool = False) -> Any:
        pieces = [str(len(keys))]
        pieces.extend(keys)
        if withscores:
            pieces.append("WITHSCORES")
        return self.execute("zdiff", *pieces)

    def zincrby(self, key: str, increment: float, member: str) -> Any:
        return self.execute("zincrby", key, str(increment), member)

    def zinter(self, *keys: str, withscores: bool = False) -> Any:
        pieces = [str(len(keys))]
        pieces.extend(keys)
        if withscores:
            pieces.append("WITHSCORES")
        return self.execute("zinter", *pieces)

    def zintercard(self, *keys: str, limit: int = None) -> Any:
        pieces = [str(len(keys))]
        pieces.extend(keys)
        if limit is not None:
            pieces.extend(["LIMIT", str(limit)])
        return self.execute("zintercard", *pieces)

    def zinterstore(self, destination: str, *keys: str) -> Any:
        return self.execute("zinterstore", destination, str(len(keys)), *keys)

    def zpopmax(self, key: str, count: int = None) -> Any:
        pieces = [key]
        if count is not None:
            pieces.append(str(count))
        return self.execute("zpopmax", *pieces)

    def zpopmin(self, key: str, count: int = None) -> Any:
        pieces = [key]
        if count is not None:
            pieces.append(str(count))
        return self.execute("zpopmin", *pieces)

    def zrandmember(
            self,
            key: str,
            count: int = None,
            withscores: bool = False
    ) -> Any:
        pieces = [key]
        if count is not None:
            pieces.append(str(count))
        if withscores:
            pieces.append("WITHSCORES")
        return self.execute("zrandmember", *pieces)

    def zmpop(
            self,
            *keys: str,
            min_=False,
            max_=False,
            count: int = None
    ) -> Any:
        pieces = [str(len(keys))]
        pieces.extend(keys)
        if (min_ and max_) or (not min_ and not max_):
            raise ValueError("min_ and max_ cannot be both True or False")
        elif min_:
            pieces.append("MIN")
        else:
            pieces.append("MAX")
        if count is not None:
            pieces.extend(["COUNT", str(count)])
        return self.execute("zmpop", *pieces)

    def zrange(
            self,
            key: str,
            start: int,
            stop: int,
            withscores: bool = False,
            rev: bool = False
    ) -> Any:
        pieces = [key, str(start), str(stop)]
        if withscores:
            pieces.append("WITHSCORES")
        if rev:
            pieces.append("REV")
        return self.execute("zrange", *pieces)

    def zrangebyscore(
            self,
            key: str,
            min_score: float,
            max_score: float,
            withscores: bool = False,
            limit: Tuple[int, int] = None
    ) -> Any:
        pieces = [key, str(min_score), str(max_score)]
        if withscores:
            pieces.append("WITHSCORES")
        if limit is not None:
            pieces.extend(["LIMIT", str(limit[0]), str(limit[1])])
        return self.execute("zrangebyscore", *pieces)

    def zrevrangebyscore(
            self,
            key: str,
            max_score: float,
            min_score: float,
            withscores: bool = False,
            limit: Tuple[int, int] = None
    ) -> Any:
        pieces = [key, str(max_score), str(min_score)]
        if withscores:
            pieces.append("WITHSCORES")
        if limit is not None:
            pieces.extend(["LIMIT", str(limit[0]), str(limit[1])])
        return self.execute("zrevrangebyscore", *pieces)

    def zrank(self, key: str, member: str, withscores: bool = False) -> Any:
        pieces = [key, member]
        if withscores:
            pieces.append("WITHSCORES")
        return self.execute("zrank", *pieces)

    def zrem(self, key: str, *members: str) -> Any:
        return self.execute("zrem", key, *members)

    def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> Any:
        return self.execute("zremrangebyscore", key, str(min_score), str(max_score))

    def zrevrank(self, key: str, member: str, withscores: bool = False) -> Any:
        pieces = [key, member]
        if withscores:
            pieces.append("WITHSCORES")
        return self.execute("zrevrank", *pieces)

    def zscan(
            self,
            key: str,
            cursor: int = 0,
            match: str = None,
            count: int = None
    ) -> Any:
        pieces = [key, str(cursor)]
        if match is not None:
            pieces.extend(["MATCH", match])
        if count is not None:
            pieces.extend(["COUNT", str(count)])
        return self.execute("zscan", *pieces)

    def zscore(self, key: str, member: str) -> Any:
        return self.execute("zscore", key, member)

    def zunion(self, *keys: str, withscores: bool = False) -> Any:
        pieces = [str(len(keys))]
        pieces.extend(keys)
        if withscores:
            pieces.append("WITHSCORES")
        return self.execute("zunion", *pieces)

    def zmscore(self, key: str, *members: str) -> Any:
        return self.execute("zmscore", key, *members)
