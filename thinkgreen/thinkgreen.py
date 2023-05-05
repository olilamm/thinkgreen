"""Main module."""

import string
import random
import ipyleaflet 
import streamlit 
import numpy
import matplotlib.pyplot 

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
            elif basemap.lower() == "terrain":
                url = 'http://mt0.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}'
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
            """Adds a raster layer to the map.

            Args:
                url (str): The URL of the raster layer.
                name (str, optional): The name of the raster layer. Defaults to 'Raster'.
                fit_bounds (bool, optional): Whether to fit the map bounds to the raster layer. Defaults to True.
            
            Returns:
                ipyleaflet.raster: Adds a raster image to the map. 
            """
            import requests

            titiler_endpoint = "https://titiler.xyz"

            r = requests.get(
                f"{titiler_endpoint}/cog/info",
                params = {
                    "url": url,
                }
            ).json()

            bounds = r["bounds"]

            r = requests.get(
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
        
        def add_image(self, path, w=250, h=250):
            """Adds a small image (like your logo) to the bottom right of the map
            Args:
            file (str): the filepath of the image
            w (int) : width of the image (defaults 250 px)
            h (int) : height of the image (defaults 250 px)
            """
            import ipywidgets as widgets

            file = open(path, "rb")
            image = file.read()
            i = widgets.Image(
                value=image,
                format='png',
                width=w,
                height=h,
            )
            
            output_widget = widgets.Output()
            output_control = ipyleaflet.WidgetControl(widget=output_widget, position='bottomright')
            self.add_control(output_control)
            with output_widget:
                display(i)

        def add_vector(self, data, name, **kwarags):
            """Adds a vector layer to the map.
            Can be GeoJson, shapefile, GeoDataFrame, etc
            Args:
                data: the vector data
                name: the type of data. example: 'GeoJson', 'Shapefile', 'GeoDataFrame'
                kwargs: Keyword arguments to pass to the layer.
            """
            if name == "GeoJson":
                self.add_geojson(self, data, name, **kwargs)
            elif name == "Shapefile":
                self.add_shp(self, data, name, **kwargs)
            elif name == "GeoDataFrame":
                self.add_geodf(self, data, name, **kwargs)
            else:
                print("This type of vector is not supported yet.")

        def add_toolbar(self, position="topright"):
            
            import ipywidgets as widgets 

            basemap = widgets.Dropdown(
            options=['ROADMAP', 'SATELLITE', 'TERRAIN'],
            value=None,
            description='Basemap:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='250px')
            )

            basemap_ctrl = ipyleaflet.WidgetControl(widget=basemap, position='topright')
            self.add_control(basemap_ctrl)
            def change_basemap(change):
                if change['new']:
                    self.add_basemap(basemap.value)

            basemap.observe(change_basemap, names='value')

            def toolbar_click(b):
                with b:
                    b.clear_output()

                    if b.icon == 'map':
                        self.add_control(basemap_ctrl)

        def add_chart(self, position="bottomleft"):
            import streamlit as st
            import ipywidgets as widgets
            import numpy as np
            import matplotlib.pyplot as plt

            chart_type = widgets.Dropdown(
                options=['BAR','LINE','AREA'],
                value=None,
                description='Chart:',
                style={'description_width': 'initial'},
                layout=widgets.Layout(width='250px')
            )

            chart_ctrl = ipyleaflet.WidgetControl(widget=chart_type, position='bottomright')
            self.add_control(chart_ctrl)
            def change_chart(change):
                if change['new']:
                    self.add_chart(chart.value)
            
            chart_type.observe(change_chart, names='value')

            file = st.file_uploader("Upload CSV", type="csv")
            if file is not None:
                data = pd.read_csv(file)
            

            if chart_type.value == 'BAR':
                st.bar_chart(data)
            elif chart_type.value == "LINE":
                st.line_chart(data)
            elif chart_type.value == "AREA":
                st.area_chart(data)

            def chart_click(c):
                with c:
                    c.clear_output()

                    if c.icon == 'map':
                        self.add_control(chart_type)






