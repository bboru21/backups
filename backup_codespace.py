from simple_settings import settings
import subprocess

def run():

  for cs in (
    settings.CODESPACE_COPTHIS,
    settings.CODESPACE_COPTHIS_WEBSITE,
    settings.CODESPACE_MERCHBAR_WEB,
  ):

    print(f"backing up files for {cs['NAME']}")

    for filename in cs['FILENAMES']:
      source = f'remote:{cs["PATH"]}/{filename}'
      target = '/Users/bryanhadromerchbar/Documents/Backups/Codespaces'

      completed_process = subprocess.run([
          'gh',
          'codespace',
          'cp',
          '-e',
          '-c',
          cs['NAME'],
          source,
          target,
      ])

      print(f"codespace cp completed with code {completed_process.returncode} for file {filename}")

    print(f"file backup complete for {cs['NAME']}")

  print("finis")

run()