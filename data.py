import random, string

def genrandstring():
  return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def serializedict(dct):
  ret = "{"
  ctr = 0
  if not dct: return "{}"
  ld = len(dct)
  for item, value in dct.items():
    ret += f'"{item}": '
    if type(value) == list:
      ret += serializelist(value)
    elif type(value) == dict:
      ret += serializedict(value)
    else:
      ret += f'"{value}"'
    ctr += 1
    if ctr < ld:
      ret += ", "
  ret += "}"
  return ret

def serializelist(lst):
  ret = "["
  if not lst:
    return "[]"
  for val in lst:
    if type(val) == list:
      ret += serializelist(val)
    elif type(val) == dict:
      ret += serializedict(val)
    else:
      ret += f'"{val}"'
    if val != lst[-1]:
      ret += ", "
  ret += "]"
  return ret

def writeTradeData(data):
  file = open("tradesav.txt", "w+")
  for dct in data:
    print(f"{dct['action']} {dct['qty']} {dct['ticker']} {dct['price']}", file=file)
  file.close()

def readTradeData():
  file = open("tradesav.txt", "r")
  res = []
  for ln in file.readlines():
    ln = ln.split(' ')
    tmp = {
      "action": ln[0],
      "qty": int(ln[1]),
      "ticker": ln[2],
      "price": float(ln[3])
    }
    res.append(tmp)
  file.close()
  return res
    
    
    
