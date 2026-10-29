"""Start both local services, wait for readiness, then open the user's browser."""
import os, shutil, socket, subprocess, sys, time, urllib.request, webbrowser
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def port_free(port):
    with socket.socket() as s:
        try:s.bind(('127.0.0.1',port));return True
        except OSError:return False

def main():
    for port in (5000,5173):
        if not port_free(port):
            print(f'Port {port} is already busy. Close the earlier project terminal, then try again.');return 1
    npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
    if not npm:print('Install Node.js LTS first.');return 1
    children=[]
    try:
        children.append(subprocess.Popen([sys.executable,'app.py'],cwd=ROOT/'backend'))
        # cmd.exe is required for npm.cmd on Windows. No user input is interpolated.
        command=['cmd.exe','/d','/c','npm.cmd','run','dev'] if os.name=='nt' else [npm,'run','dev']
        children.append(subprocess.Popen(command,cwd=ROOT/'frontend'))
        for _ in range(60):
            if any(p.poll() is not None for p in children):raise RuntimeError('A server stopped. Check the error above.')
            try:
                with urllib.request.urlopen('http://127.0.0.1:5173/api/v1/health',timeout=1) as r:
                    if r.status==200:break
            except Exception:time.sleep(.5)
        else:raise RuntimeError('Server did not become ready within 30 seconds.')
        print('\nShop ready: http://localhost:5173\nKeep this terminal open. Press Ctrl+C to stop both servers.\n')
        webbrowser.open('http://localhost:5173')
        while all(p.poll() is None for p in children):time.sleep(1)
    except KeyboardInterrupt:print('\nStopping Everyday Shop…')
    except Exception as e:print(str(e));return 1
    finally:
        for p in children:
            if p.poll() is None:
                if os.name=='nt':subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                else:p.terminate()
    return 0
if __name__=='__main__':sys.exit(main())
