import win32com.client
inst = win32com.client.Dispatch("CpUtil.CpCybos")
print(inst.IsConnect) # 연결이 됬는지 확인하는 코드