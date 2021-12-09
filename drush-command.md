```
root@b15318351296:/var/www/html/sites/default# drush -u 1 iduF grinnell:19237 AddXML --title="note" --contents="109 of 176 slides from the Grinnell Chamber of Commerce collection have been added to the Poweshiek History Preservation Project. A physical copy of all of the slides can be found at Drake Community Library Archives in Grinnell, Iowa." --xpath="/mods:mods"
root@b15318351296:/var/www/html/sites/default# drush -u 1 iduF grinnell:19237 SelfTransform --reorder
```

The results look GREAT!