### USAGE ##############################################################
___
```python
path = "/path/to/scene-file"
sd = SceneData(path)

timeline_binary = sd.get_timeline_xml
timeline = sd.get_timeline_xml_tree()
(
  timeline_status: str,     # "has_timeline", "no_timeline" 
  image_type: Optional[str],# "animation", "dynamic", "static", None
  sfx_status: bool,         # True if sfx found
  duration: int
) = sd.get_timeline_info()
```
