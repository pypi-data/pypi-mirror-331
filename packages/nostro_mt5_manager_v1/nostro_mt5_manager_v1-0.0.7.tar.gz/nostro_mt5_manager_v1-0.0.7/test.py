import os
from nostro_mt5_manager_v1.manager import Manager

manager = Manager(
    mt5_server="38.240.39.119:443",
    mt5_login=2002,
    mt5_password="O@ZuHx3v",
)
connected = manager.connect()
if not connected["status"] == "connected":
    print(f"TimeoutError")

isReset = manager.reset_to_initial_balance(576132, 2500)
print(f"Is Reset :{isReset}")
