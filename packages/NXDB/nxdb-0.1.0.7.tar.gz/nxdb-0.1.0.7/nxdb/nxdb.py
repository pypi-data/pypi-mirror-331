import os
import threading

class _Types():
    def __init__(self):
        self.ACTION_ADD_VALUE = -101
        self.ACTION_REMOVE_VALUE = -102
        self.ACTION_READ_VALUES = -103
        self.ACTION_READ_VALUE = -104
        self.ACTION_SET_VALUE = -105
        self.ACTION_GET_LAST_ID = -106
types = _Types()

class _Action():
    def __init__(self, type, action_id, args={}):
        self.type = type
        self.action_id = action_id
        self.args = args

class DatabaseNotFound(Exception): pass
class HeaderNotFound(Exception): pass
class ServiceNotWorking(Exception): pass
class NotNXDBFile(Exception): pass

_specsymbols = [chr(0x88), chr(0xFF)]

def _read(filename):
    with open(filename, 'rb') as f:
        text = f.read()
    if text.split(b'\n')[0] != b'DOTNXDB':
        raise NotNXDBFile()
    line, rawresult, i = 0, '', 0
    while i < len(text):
        symbol = chr(text[i])
        if symbol == '\n':
            line += 1
            if line == 1:
                i += 1
                continue
        if line != 0:
            rawresult = rawresult + symbol
        i += 1

    valresult, stepresult, ignore, i = [], '', False, 0
    while i < len(rawresult):
        symbol = rawresult[i]
        if ignore == True:
            stepresult += symbol
            ignore = False
            i += 1
            continue
        elif symbol == '\\':
            ignore = True
            i += 1
            continue
        elif symbol == chr(0xFF):
            valresult.append(stepresult)
            stepresult = ''
        else:
            stepresult += symbol
        i += 1

    preresult, i = [], 0
    while i < len(valresult):
        item = valresult[i]
        splitted, ignore, itemresult, stepresult, x = [], False, [], '', 0
        while x < len(item):
            symbol = item[x]
            if ignore == True:
                stepresult += symbol
                ignore = False
                x += 1
                continue
            elif symbol == '\\':
                ignore = True
                x += 1
                continue
            elif symbol != chr(0x88):
                stepresult += symbol
            if symbol == chr(0x88) or x == len(item) - 1:
                itemresult.append(stepresult)
                stepresult = ''
            x += 1
        preresult.append(itemresult)
        i += 1

    result, i, itemresult = {}, 0, {}
    while i < len(preresult):
        item, key, value, stepresult, x = preresult[i], 0, {}, [], 0
        while x < len(item):
            if x == 0:
                key = int(item[x])
                x += 1
                continue
            stepresult.append(item[x])
            if x / 2 == round(x / 2):
                itemresult[stepresult[0]] = stepresult[1]
                stepresult = []
            x += 1
        result[key] = itemresult
        itemresult = {}
        i += 1
    return result

def _write(filename, data):
    text = b'DOTNXDB\n'
    for itemk, itemv in data.items():
        text = text + str(itemk).encode()
        for k, v in itemv.items():
            text = text + b'\x88' + str(k).encode()
            text = text + b'\x88' + str(v).encode()
        text = text + b'\xff'
    with open(filename, 'wb') as f:
        f.write(text)

class Service():
    def __init__(self, filename):
        self.queue = []
        self.filename = filename + '.nxdb'
        if not os.path.exists(self.filename):
            raise DatabaseNotFound(f'Try to use "nxdb-cli create_db {filename}" in terminal')
        self.working = False
        self._lastid = -1
        self.ids = {}
    def _new_action(self):
        if not self.working:
            raise ServiceNotWorking()
        self._lastid += 1
        return self._lastid
    def _wait_for_return(self, id):
        while True:
            if id in self.ids:
                return self.ids[id]
    def add_value(self, key, values):
        id = self._new_action()
        self.queue.append(_Action(types.ACTION_ADD_VALUE, id, {'key': key, 'values': values}))
    def read_values(self):
        id = self._new_action()
        self.queue.append(_Action(types.ACTION_READ_VALUES, id))
        return self._wait_for_return(id)
    def remove_value(self, key):
        id = self._new_action()
        self.queue.append(_Action(types.ACTION_REMOVE_VALUE, id, {'key': key}))
    def get_last_id(self):
        id = self._new_action()
        self.queue.append(_Action(types.ACTION_GET_LAST_ID, id, {}))
        return self._wait_for_return(id)
    def _start_service(self):
        while True:
            if not self.working:
                break
            if len(self.queue) > 0:
                action = self.queue[0]
                # Start processing
                if action.type == types.ACTION_ADD_VALUE:
                    db = _read(self.filename)
                    item = {}
                    for k, v in action.args['values'].items():
                        item[k] = v
                    db[action.args['key']] = item
                    _write(self.filename, db)
                elif action.type == types.ACTION_READ_VALUES:
                    self.ids[action.action_id] = _read(self.filename)
                elif action.type == types.ACTION_GET_LAST_ID:
                    max_id = -1
                    for k, v in _read(self.filename).items():
                        if k > max_id: max_id = k
                    self.ids[action.action_id] = max_id
                elif action.type == types.ACTION_REMOVE_VALUE:
                    db = _read(self.filename)
                    if action.args['key'] in db:
                        db.pop(action.args['key'])
                        _write(self.filename, db)
                    else: pass
                # End processing
                self.queue.pop(0)
    def start_service(self):
        self.working = True
        self.thread = threading.Thread(target=self._start_service)
        self.thread.start()
    def stop_service(self):
        self.working = False
