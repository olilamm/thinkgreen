"""Main module."""

import string
import random
import ipyleaflet 

class Map(ipyleaflet.Map):
    
        def __init__(self, center=[20, 0], zoom=2, **kwargs) -> None:

            if "scroll_wheel_zoom" not in kwargs:
                kwargs["scroll_wheel_zoom"] = True

            super().__init__(center=center, zoom=zoom, **kwargs)

            if "height" not in kwargs:
                self.layout.height = "500px"
            else:
                self.layout.height = kwargs["height"]

            if "fullscreen_control" not in kwargs:
                kwargs["fullscreen_control"] = True
            if kwargs["fullscreen_control"]:
                self.add_fullscreen_control()
            
            if "layers_control" not in kwargs:
                kwargs["layers_control"] = False
            if kwargs["layers_control"]:
                self.add_layers_control()

        def add_search_control(self, position="topleft", **kwargs):
            """Adds a search control to the map.
            Args:
                kwargs: Keyword arguments to pass to the search control.
            
            Returns:
                ipyleaflet.SearchControl: The search control.
            """
            if "url" not in kwargs:
                kwargs["url"] = 'https://nominatim.openstreetmap.org/search?format=json&q={s}'
        

            search_control = ipyleaflet.SearchControl(position=position, **kwargs)
            self.add_control(search_control)

        def add_draw_control(self, **kwargs):
            """Adds a draw control to the map.
            Args:
                kwargs: Keyword arguments to pass to the draw control.
            
            Returns:
                ipyleaflet.DrawControl: Draw control.
            """
            draw_control = ipyleaflet.DrawControl(**kwargs)

            draw_control.polyline =  {
                "shapeOptions": {
                    "color": "#6bc2e5",
                    "weight": 8,
                    "opacity": 1.0
                }
            }
            draw_control.polygon = {
                "shapeOptions": {
                    "fillColor": "#6be5c3",
                    "color": "#6be5c3",
                    "fillOpacity": 1.0
                },
                "drawError": {
                    "color": "#dd253b",
                    "message": "Oups!"
                },
                "allowIntersection": False
            }
            draw_control.circle = {
                "shapeOptions": {
                    "fillColor": "#efed69",
                    "color": "#efed69",
                    "fillOpacity": 1.0
                }
            }
            draw_control.rectangle = {
                "shapeOptions": {
                    "fillColor": "#fca45d",
                    "color": "#fca45d",
                    "fillOpacity": 1.0
                }
            }

            self.add_control(draw_control)

        def add_layers_control(self, position="topright"):
            """Adds a layers control to the map.
            Args:
                kwargs: Keyword arguments to pass to the layers control.
            
            Returns: 
                ipyleaflet.LayersControl: The layers control.
            """
            layers_control = ipyleaflet.LayersControl(position=position)
            self.add_control(layers_control)

        def add_fullscreen_control(self, position="topleft"):
            """Adds a fullscreen control to the map.
            Args:
                kwargs: Keyword arguments to pass to the fullscreen control.

            Returns:
                ipyleaflet.FullscreenControl: Allows control of screensize.
            """
            fullscreen_control = ipyleaflet.FullScreenControl(position=position)
            self.add_control(fullscreen_control)

        def add_tile_layer(self, url, name, attribution="", **kwargs):
            """Adds a tile layer to the map.
            Args:
                url (str): The URL template of the tile layer.
                attribution (str): The attribution of the tile layer.
                name (str, optional): The name of the tile layer. Defaults to "OpenStreetMap".
                kwargs: Keyword arguments to pass to the tile layer.

            Returns: 
                ipyleaflet.TileLayer: Adds a new layer to the map.
            """
            tile_layer = ipyleaflet.TileLayer(url=url, attribution=attribution, name=name, **kwargs)
            self.add_layer(tile_layer)

        def add_basemap(self, basemap, **kwargs):

            import xyzservices.providers as xyz

            if basemap.lower() == "roadmap":
                url = 'http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}'
                self.add_tile_layer(url, name=basemap, **kwargs)
            elif basemap.lower() == "satellite":
                url = 'http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}'
                self.add_tile_layer(url, name=basemap, **kwargs)
            else:
                try:
                    basemap = eval(f"xyz.{basemap}")
                    url = basemap.build_url()
                    attribution = basemap.attribution
                    self.add_tile_layer(url, name=basemap.name, attribution=attribution, **kwargs)
                except:
                    raise ValueError(f"Basemap '{basemap}' not found.")
        

        def add_geojson(self, data, **kwargs):
            """Adds a GeoJSON layer to the map.
            Args:
                data (dict): The GeoJSON data.
                kwargs: Keyword arguments to pass to the GeoJSON layer.

            Returns:
                ipyleaflet.Geojson: Adds a GeoJSON layer to map. 
            """
            import json
            
            #for file paths:
            if isinstance(data, str):
                with open(data, "r") as f:
                    data = json.load(f)

            geojson = ipyleaflet.GeoJSON(data=data, **kwargs)
            self.add_layer(geojson)
        
        def add_shp(self, data, name='Shapefile', **kwargs):
            """Adds a Shapefile layer to the map.

            Args:
                data (str): The path to the Shapefile.
            
            Returns:
                ipyleaflet.ShapeFile: Adds a shapefile to map.
            """
            import geopandas as gpd
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
            self.add_geojson(geojson, name=name, **kwargs)

        def add_raster(self, url, name='Raster', fit_bounds=True, **kwargs):
             """Adds a Raster layer to the map.

            Args:
                url (str): The URL of the raster layer.
                name (str): The name of the raster layer. Defaults to the name of 'Raster'
                fit_bounds(bool): Fits the raster layer to the bounds of the map. Defaulted to True.
            
            Returns:
                ipyleaflet.Raster: Adds a raster layer to map.
            """
             titiler_endpoint = "https://titiler.xyz"

            r = httpx.get(
                f"{titiler_endpoint}/cog/info",
                params = {
                    "url": url,
                }
            ).json()

            bounds = r["bounds"]

            r = httpx.get(
                f"{titiler_endpoint}/cog/tilejson.json",
                params = {
                    "url": url,
                }
            ).json()

            tile = r["tiles"][0]

            self.add_tile_layer(url=tile, name=name, **kwargs)

            if fit_bounds:
                bbox = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
                self.fit_bounds(bbox)

        def add_vector(
            self,
            filename,
            layer_name="Untitled",
            bbox=None,
            mask=None,
            rows=None,
            style={},
            hover_style={},
            style_callback=None,
            fill_colors=["black"],
            info_mode="on_hover",
            encoding="utf-8",
            **kwargs,
        ):
            """Adds any geopandas-supported vector dataset to the map.

            Args:
                filename (str): Either the absolute or relative path to the file or URL to be opened, or any object with a read() method (such as an open file or StringIO).
                layer_name (str, optional): The layer name to use. Defaults to "Untitled".
                bbox (tuple | GeoDataFrame or GeoSeries | shapely Geometry, optional): Filter features by given bounding box, GeoSeries, GeoDataFrame or a shapely geometry. CRS mis-matches are resolved if given a GeoSeries or GeoDataFrame. Cannot be used with mask. Defaults to None.
                mask (dict | GeoDataFrame or GeoSeries | shapely Geometry, optional): Filter for features that intersect with the given dict-like geojson geometry, GeoSeries, GeoDataFrame or shapely geometry. CRS mis-matches are resolved if given a GeoSeries or GeoDataFrame. Cannot be used with bbox. Defaults to None.
                rows (int or slice, optional): Load in specific rows by passing an integer (first n rows) or a slice() object.. Defaults to None.
                style (dict, optional): A dictionary specifying the style to be used. Defaults to {}.
                hover_style (dict, optional): Hover style dictionary. Defaults to {}.
                style_callback (function, optional): Styling function that is called for each feature, and should return the feature style. This styling function takes the feature as argument. Defaults to None.
                fill_colors (list, optional): The random colors to use for filling polygons. Defaults to ["black"].
                info_mode (str, optional): Displays the attributes by either on_hover or on_click. Any value other than "on_hover" or "on_click" will be treated as None. Defaults to "on_hover".
                encoding (str, optional): The encoding to use to read the file. Defaults to "utf-8". 
            """
            if not filename.startswith("http"):
                filename = os.path.abspath(filename)
            else:
                filename = github_raw_url(filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".shp":
                self.add_shp(
                    filename,
                    layer_name,
                    style,
                    hover_style,
                    style_callback,
                    fill_colors,
                    info_mode,
                    encoding,
                )
            elif ext in [".json", ".geojson"]:
                self.add_geojson(
                    filename,
                    layer_name,
                    style,
                    hover_style,
                    style_callback,
                    fill_colors,
                    info_mode,
                    encoding,
                )
            else:
                geojson = vector_to_geojson(
                    filename,
                    bbox=bbox,
                    mask=mask,
                    rows=rows,
                    epsg="4326",
                    **kwargs,
                )

                self.add_geojson(
                    geojson,
                    layer_name,
                    style,
                    hover_style,
                    style_callback,
                    fill_colors,
                    info_mode,
                    encoding,
                )




def generate_random_string(length=10, upper=False, digits=False, punctuation=False):
    """Generates a random string of a given length.
    Args:
        length (int, optional): The length of the string to generate. Defaults to 10.
        upper (bool, optional): Whether to include uppercase letters. Defaults to False.
        digits (bool, optional): Whether to include digits. Defaults to False.
        punctuation (bool, optional): Whether to include punctuation. Defaults to False.
    Returns:
        str: The generated string.
    """
    letters = string.ascii_lowercase
    if upper:
        letters += string.ascii_uppercase
    if digits:
        letters += string.digits
    if punctuation:
        letters += string.punctuation
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def generate_lucky_number(length=1):
    """Generates a random number of a given length.
    Args:
        length (int, optional): The length of the number to generate. Defaults to 1.
    Returns:
        int: The generated number.
    """

    result_str = ''.join(random.choice(string.digits) for i in range(length))
    return int(result_str)
