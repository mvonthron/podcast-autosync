# -*- encoding: utf-8 -*-

#
## Example of rules
#
# rules = {
#   "AB42-CD79": {                                                      # ID of the device, see "autosync.py --new-device"
#     "name": None,                                                     # if None, we will use device's declared name
#     "sync-dirs": [
#       ("/home/user/podcast/a_show/", "music/podcast/a_show"),         # with trailing slash on source ! (rsync format)
#     ]
#   },
#
#   "CD31-E415": {                                                      # another device list of rules
#     "name": "Fancy-name",                                             # why not
#     "sync-dirs": [
#       ("/home/user/pictures/any/", "DCIM/any"),                       # of course we can sync any type of data
#       ("/home/user/music/to_go/", "MUSIC/"),
#     ]
#   },
# }

#
rules = {
  "C890-7C63": {
    "name": None,                                                       # if None, we will use device's declared name
    "sync-dirs": [
      ("/home/manuel/musique/__radio/Ruquier/", "MUSIC/Radio/Ruquier"),  # with trailing slash on source !
      ("/home/manuel/musique/__radio/Canteloup/", "MUSIC/Radio/Canteloup"),
    ]
  }
}
