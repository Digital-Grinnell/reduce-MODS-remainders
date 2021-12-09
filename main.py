import fileinput
import shutil
import os
import json
import traceback
import sys
import logging
import re
from datetime import datetime

text_targets = [
  '"subject": [{"@authority": "lcsh"}, {"@authority": "lcsh"}]',
  '"subject": [{"@authority": "lcsh"}]',
  '"subject": {"@authority": "lcsh"}',
  '"relatedItem": [{"titleInfo": {"title": "Digital Grinnell"}}]',
  '{"relatedItem": [{"titleInfo": {"title": "Digital Grinnell"}}]}',
  '{ }',
  '{}'
]

key_targets = [
  "extension"
]

def create_temporary_copy(tpath):
  # temp_dir = tempfile.gettempdir()
  # temp_path = os.path.join(., 'remainder.tmp')
  temp_path = 'remainder.tmp'
  shutil.copy2(tpath, temp_path)
  return temp_path

def clean_json(string):
  string = str.replace(string, "}, }", "}}")
  string = str.replace(string, "{, ", "{")
  string = re.sub(",[ \t\r\n]+}", "}", string)
  string = re.sub(",[ \t\r\n]+]", "]", string)
  string = str.replace(string, ", , ", ", ")
  return string

# check intended contents of the drush command before issue, if it's not a string, something is probably wrong.
def check_contents(val, pid):
  if type(val) is not str:
    logging.error("Object {}'s remaining MODS metadata included an unanticipated list or dict structure. That element will be skipped!".format(pid))
    return False
  return True

# make iduF commands to create new `mods|extension|dg_private_note` elements for missing records of these forms:
# grinnell_11294_MODS.remainder.clean:{"relatedItem": {"@type": "admin", "note": "Information on correct address of the house provided by Milton Severe, 11 May 2016."}}
# grinnell_6126_MODS.remainder.clean:{"relatedItem": [{"@type": "admin", "note": "Identification of Ed McGuire provided via annotation form by an unknown user."}]}
# grinnell_6128_MODS.remainder.clean:{"relatedItem": [{"@type": "admin", "note": {"#text": "Additional names of cast provided via Facebook by Beth Czechowski Cox.", "@type": "source note"}}]}
def related(d, dir, pid):
  
  if d["@type"] == "admin":
    val = d["note"]
    if type(val) is dict:
      v = d["note"]["#text"]
    else:
      v = val
    if check_contents(v, pid):
      cmd = 'drush -u 1 iduF {} AddXML --title="dg_private_note" --xpath="/mods:mods/mods:extension" --contents="{}" \n'.format(
        pid, v)
      cmd = cmd + 'drush -u 1 iduF {} SelfTransform --reorder \n'.format(pid)
      with open(os.path.join(dir.decode("utf-8"), "iduF-AddXML-private.cmd"), "a") as idu:
        idu.write(cmd)
    return
  
  if d["@type"] == "host":
    val = d["identifier"]
    if type(val) is dict:
      v = d["identifier"]["#text"]
    else:
      v = val
    if check_contents(v, pid):
      cmd = 'drush -u 1 iduF {} AddXML --title="note" --xpath="/mods:mods" --contents="{}" \n'.format(
        pid, v)
      cmd = cmd + 'drush -u 1 iduF {} SelfTransform --reorder \n'.format(pid)
      with open(os.path.join(dir.decode("utf-8"), "iduF-AddXML-relatedItem.cmd"), "a") as idu:
        idu.write(cmd)

def make_idu_commands(dir, pid, json):
  cmd = ""

  # make iduF commands for missing `abstract` fields
  if "abstract" in json.keys():
    typ = type(json["abstract"])
    if typ is list:
      abstract = ""
      for val in json["abstract"]:
        if check_contents(val, pid):
          abstract = abstract + "  " + val
      cmd = cmd + 'drush -u 1 iduF {} AddXML --title="note" --xpath="/mods:mods" --contents="{}" \n'.format(pid, abstract.strip())
      cmd = cmd + 'drush -u 1 iduF {} SelfTransform --reorder \n'.format(pid)
      with open(os.path.join(dir.decode("utf-8"),"iduF-AddXML-abstract.cmd"), "a") as idu:
        idu.write(cmd)


  # make iduF commands for missing `originInfo` fields
  if "originInfo" in json.keys():
    typ = type(json["originInfo"])
    if typ is dict:
      for key, val in json["originInfo"].items():
        if check_contents(val, pid):
          cmd = cmd + 'drush -u 1 iduF {} AddXML --title="{}" --xpath="/mods:mods/mods:originInfo" --contents="{}" \n'.format(pid, key, val)
          cmd = cmd + 'drush -u 1 iduF {} SelfTransform --reorder \n'.format(pid)
          with open(os.path.join(dir.decode("utf-8"),"iduF-AddXML-originInfo.cmd"), "a") as idu:
            idu.write(cmd)

  # make iduF commands for missing `note` fields
  if "note" in json.keys():
    typ = type(json["note"])
    if typ is list:
      for val in json["note"]:
        if check_contents(val, pid):
          cmd = cmd + 'drush -u 1 iduF {} AddXML --title="note" --xpath="/mods:mods" --contents="{}" \n'.format(pid, val)
          cmd = cmd + 'drush -u 1 iduF {} SelfTransform --reorder \n'.format(pid)
          with open(os.path.join(dir.decode("utf-8"), "iduF-AddXML-note.cmd"), "a") as idu:
            idu.write(cmd)
    else:
      val = json["note"]
      if check_contents(val, pid):
        cmd = cmd + 'drush -u 1 iduF {} AddXML --title="note" --xpath="/mods:mods" --contents="{}" \n'.format(pid, val)
        cmd = cmd + 'drush -u 1 iduF {} SelfTransform --reorder \n'.format(pid)
        with open(os.path.join(dir.decode("utf-8"),"iduF-AddXML-note.cmd"), "a") as idu:
          idu.write(cmd)

  # make iduF commands to create new `mods|extension|dg_private_note` elements for missing records of these forms:
  # grinnell_11294_MODS.remainder.clean:{"relatedItem": {"@type": "admin", "note": "Information on correct address of the house provided by Milton Severe, 11 May 2016."}}
  # grinnell_6126_MODS.remainder.clean:{"relatedItem": [{"@type": "admin", "note": "Identification of Ed McGuire provided via annotation form by an unknown user."}]}
  # grinnell_6128_MODS.remainder.clean:{"relatedItem": [{"@type": "admin", "note": {"#text": "Additional names of cast provided via Facebook by Beth Czechowski Cox.", "@type": "source note"}}]}
  # grinnell_185_MODS.remainder.clean:{"relatedItem": [{"@type": "host", "identifier": {"#text": "Des Moines Register, 1859?", "@type": "uri"}}]}
  if "relatedItem" in json.keys():
    typ = type(json["relatedItem"])
    if typ is not list:
      related(json["relatedItem"], dir, pid)
    else:
      for d in json["relatedItem"]:
        related(d, dir, pid)
  
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
  
  print('Number of arguments:', len(sys.argv), 'arguments.')
  print('Argument List:', str(sys.argv))
  
  if not len(sys.argv) == 2:
    sys.exit("ERROR: You must specify exactly 1 command line arguments, the path to the directory of .remainder files to be processed.")
  
  path = sys.argv[1]
  
  FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
  logging.basicConfig(filename="{}.log".format(path), level=logging.DEBUG, format=FORMAT)
  logging.getLogger().addHandler(logging.StreamHandler())
  
  print("INFO: New logfile {}.log has been opened in the working directory.".format(path))
  logging.info(datetime.now())

  directory = os.fsencode(path)

  for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".remainder"):
      fullpath = os.path.join(directory.decode("utf-8"), filename)
      ns, pidn, junk = filename.split("_")
      pid = "{}:{}".format(ns, pidn)
      cleaned_path = fullpath + ".clean"

      temp = create_temporary_copy(fullpath)

      # First, open and read the temporary file as text, remove all text_targets found.
      try:
        with open(temp, "r") as remainder:
          logging.info("'{}' remainder file found and opened to remove text targets.".format(fullpath))
          for target in text_targets:
            for lines in fileinput.input([temp], inplace=True):
              print(lines.replace(target, ""), end='')

      except Exception as e:
        logging.error(traceback.format_exc())
        sys.exit(e)

      # Is there anything left?
      size = os.path.getsize(temp)
      if size == 0:
        logging.info("There is nothing left of '{}' after removing text targets!".format(fullpath))
      else:
        
        # Now, re-open the temp file and read as json, remove entire keys.
        try:
          with open(temp, "r") as remainder:
            logging.info("'{}' remainder file found and opened to remove key targets.".format(fullpath))
            jso = remainder.read()
            
            c = clean_json(jso)
            
            try:
              data = json.loads(c)
              for target in key_targets:
                if target in data:
                  del data[target]
              # Is there anything left?
              size = len(data)
              if size == 0:
                logging.info("There is nothing left of '{}' after removing text and key targets!".format(fullpath))
              else:
                # write a new .clean file
                try:
                  with open(cleaned_path, "w") as clean:
                    clean.write(json.dumps(data))
                    logging.info("'{}' clean file written.".format(cleaned_path))
                except Exception as e:
                  logging.error(traceback.format_exc())
                  sys.exit(e)

                # ...and append to corresponding commands iduF-AddXML-*.cmd files
                try:
                  commands = make_idu_commands(directory, pid, data)
                except Exception as e:
                  # logging.error(traceback.format_exc())
                  logging.error("Object {}'s remaining MODS metadata caused parsing issues and will be skipped!".format(pid))
                  pass

            except Exception as e:
              # logging.error(traceback.format_exc())
              logging.error("Object {}'s remaining MODS metadata caused parsing issues and will be skipped!".format(pid))
              pass
             
        except Exception as e:
          logging.error(traceback.format_exc())
          sys.exit(e)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
