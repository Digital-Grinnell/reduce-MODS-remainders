# reduce-MODS-remainders

This repository and the `main.py` script should be used to analyze and remediate "remainders", elements of old MODS metadata records that were not recognized during the _Digital.Grinnell_ metadata review process conducted in 2020-2021. 

The `main.py` script can be easily configured and run from _PyCharm_ using an input parameter of the form: `/Volumes/DG-Metadata-Review-2020-r1/<collection-PID>`.  Note that parameters of this form are only valid if the desktop computer hosting this repository has `//Storage/Library/AllStaff/DG-Metadata-Review-2020-r1` mounted as `/Volumnes/DG-Metadata-Review-2020-r1`. 

The script will generate several pieces of output into the corresponding `/Volumes/DG-Metadata-Review-2020-r1/<collection-PID>` directory.  The most important are command shell files named `iduF-AddXML-*.cmd`, where `*` can be:

  - `note`, 
  - `private`, 
  - `relatedItem`, 
  - `abstract`, or 
  - `originInfo`. 

Each of the generated `iduF-AddXML-*.cmd` command files will contain a series of `iduF AddXML` commands designed to re-populate "remainder" elements back into objects' MODS records.  Each such file should be reviewed and, if acceptable, processed using a command stream like:

```markdown
cd /var/www/html/sites/default
source /mnt/metadata-review/<collection-PID>/iduF-AddXML-<type>.cmd
```

# Change History

## Collection Processing

This table is intended to record progress as collections are processed using the `main.py` script found in this repository.  See [Exporting, Editing & Replacing MODS Datastreams: Technical Details](https://static.grinnell.edu/dlad-blog/posts/070-exporting-editing-replacing-mods-datastreams-technical-details/) for details.  

| Collection | Date | Status |
| --- | --- | --- |
| phpp-dcl | 2021-Dec-8 | Complete |
| social-justice | 2021-Dec-8 | Complete |
| phpp-oral-history | 2021-Dec-8 | Complete |
| college-buildings | 2021-Dec-8 | Complete |
| college-handbooks | 2021-Dec-8 | Complete |
| college-history | 2021-Dec-8 | Complete |
| db2d | 2021-Dec-8 | Complete |
| faculty-scholarship | 2021-Dec-8 | Complete |
| grinnell-in-china | 2021-Dec-8 | Complete.  Needs review.  See 17439 |
| gwcc | 2021-Dec-8 | Complete |
| kleinschmidt | 2021-Dec-9 | Complete |
| phpp-community | 2021-Dec-9 | Complete |
| phpp-ghm | 2021-Dec-14 | Complete |

*Note that `Complete` in the above table means that the script was run, and generated `iduF-AddXML-*.cmd` files were reviewed, edited, and run against the target collection.  **Some review of these collections may still be prudent!** 

## Duplicate MODS Elements

In a handful of the collections listed here I found lots of duplication of _MODS_ elements, mostly `note` elements.  There's a quick and simple fix for these.  One example, run from the _Apache_ container on _DGDocker1_...

```markdown
drush -u 1 iduF grinnell:1-40000 RemoveDuplicateElements --collection="*china"
```

The above command was specified to deal specifically with all objects in the `grinnell-in-china` collection.

## Compound Object _Group Record_ Headings

During evaluation of records touched by this script I found that some compound parent objects were not displaying the _Group Record_ sub-heading mentioned in [Digital.Grinnell Transforms](https://static.grinnell.edu/dlad-blog/posts/114-digital.grinnell-transforms/).  

I devised a quick fix for such compound parents in the form of a _drush_ `iduF` command of the form:

`drush -u 1 iduF grinnell:12423 AddXML --title="mods:CModel" --xpath="/mods:mods/mods:extension" --contents="islandora:compoundCModel" --dsid=MODS`

That particular command produced this output...

```markdown
root@b15318351296:/var/www/html/sites/default# drush -u 1 iduF grinnell:12423 AddXML --title="mods:CModel" --xpath="/mods:mods/mods:extension" --contents="islandora:compoundCModel" --dsid=MODS
Ok, iduF command 'AddXML' was verified on 3-Dec-2021.                                                                                                                                                       [status]
icu_drush_prep will consider only objects modified with a yyyy-mm-dd local time matching 2*.                                                                                                                [status]
Starting operation for PID 'grinnell:12423' and --repeat='0' at 12:20:06.                                                                                                                                   [status]
Fetching all valid object PIDs in the specified range.                                                                                                                                                      [status]
Completed fetch of 1 valid object PIDs from Solr.                                                                                                                                                           [status]
Progress: iduFix - AddXML
icu_Connect: Connection to Fedora repository as 'System Admin' is complete.                                                                                                                                 [status]
[==============================================================================================================================================================================================================] 100%
Completed 1 'iduFix - AddXML' operations at 12:20:16.                                                                                                                                                       [status]

```

