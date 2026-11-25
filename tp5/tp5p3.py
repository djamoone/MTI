
import threading


class Singleton:
    instance = None  # static attribute of the class

    def __new__(cls):
        """Standard Python construction method."""
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance


# 1. Unique file writer singleton
class UniqueFileWriter:
    _instance = None

    def __new__(cls, filepath="output.txt"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._filepath = filepath
            cls._instance._file = open(filepath, "a", encoding="utf-8")
        return cls._instance

    def write(self, data: str):
        self._file.write(data)
        self._file.flush()

    def close(self):
        if self._file and not self._file.closed:
            self._file.close()
            UniqueFileWriter._instance = None


# 2. General exclusive connection/resource singleton (not tied to a specific DB)
class UniqueResourceConnection:
    _instance = None

    def __new__(cls, endpoint="resource://default"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._endpoint = endpoint
            cls._instance._connected = True
            print(f"Opened exclusive connection to {endpoint}")
        return cls._instance

    def send(self, payload: str):
        if not self._connected:
            raise RuntimeError("Connection is closed.")
        print(f"[{self._endpoint}] Sending: {payload}")

    def close(self):
        if self._connected:
            self._connected = False
            print(f"Closed exclusive connection to {self._endpoint}")
            UniqueResourceConnection._instance = None


# 3. Bounded simultaneous access (up to N concurrent holders for a shared resource)
class BoundedResourcePoolAccess:
    def __init__(self, resource_name: str, max_simultaneous: int = 2):
        self.resource_name = resource_name
        self._semaphore = threading.Semaphore(max_simultaneous)
        self._lock = threading.Lock()
        self._active = 0

    def use_resource(self, client_id: str, action: str):
        self._semaphore.acquire()
        try:
            with self._lock:
                self._active += 1
                print(f"[{self.resource_name}] {client_id} started '{action}' (active: {self._active})")
            # Perform work on the shared resource
        finally:
            with self._lock:
                self._active -= 1
                print(f"[{self.resource_name}] {client_id} finished '{action}' (active: {self._active})")
            self._semaphore.release()


if __name__ == "__main__":
    # Base Singleton test
    s1 = Singleton()
    s2 = Singleton()
    assert s1 is s2
    print("Base Singleton:", s1, s2)

    # Unique file writer test
    fw1 = UniqueFileWriter("demo_log.txt")
    fw2 = UniqueFileWriter("demo_log.txt")
    assert fw1 is fw2
    fw1.write("Hello Singleton file\n")
    fw1.close()

    # General unique resource connection test
    rc1 = UniqueResourceConnection("service://storage-node")
    rc2 = UniqueResourceConnection("service://storage-node")
    assert rc1 is rc2
    rc1.send("PING")
    rc2.send("STATUS")
    rc1.close()

    # Bounded simultaneous access test (max 2 at once)
    pool = BoundedResourcePoolAccess("SharedResource", max_simultaneous=2)
    threads = [
        threading.Thread(target=pool.use_resource, args=(f"Client-{i}", "read/write"))
        for i in range(4)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()