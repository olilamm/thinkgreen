"""Main module."""

import string
import random
import ipyleaflet 
import streamlit
import numpy
import matplotlib
import ipywidgets as widgets

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
                ipyleaflet.LayersControl: The search control.   
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
            """Adds a base layer to the map.

            Args:
                basemap (dict): The basemap layer from an xyz url.

            Returns:
                xyzservices.providers: Adds a tile layer as a basemap.
            """

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

            Returns:
                ipywidgets.image: Adds an image to the map. 
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

            Returns:
                ipyleaflet.vector: Adds a vector layer to the map. 
            """
            if name == "GeoJson":
                self.add_geojson(self, data, name, **kwargs)
            elif name == "Shapefile":
                self.add_shp(self, data, name, **kwargs)
            elif name == "GeoDataFrame":
                self.add_geodf(self, data, name, **kwargs)
            else:
                print("This type of vector is not supported yet.")

        def add_toolbar(self, position="topright", **kwargs):
            """Adds a toolbar using ipywidgets to change the basemap.

            Args:
                m (thinkgreen.Map, optional): The dropdown widget.

            Returns:
                ipywidgets: The tool GUI widget
            """
            
            import ipywidgets as widgets 
            allowed_positions = ["topleft", "topright", "bottomleft", "bottomright"]

            if position not in allowed_positions:
                raise Exception(f"position must be one of {allowed_positions}")
            
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

        def add_plot(self, x, y, **kwargs):
            """Add a plot to the map.

            Args:
                x (str, optional): Data to use for the x-axis.
                y (str, optional): Data to use for the y-axis.
                **kwargs: Other keyword arguments for ipywidgets.HTML().

            Returns:
                matplotlib.plot: Generates a plot graph. 
            """

            import matplotlib.pyplot as plt
            import numpy as np

            plt.style.use('_mpl-gallery')

            # plot
            fig, ax = plt.subplots()
            ax.plot(x, y, linewidth=2.0)
            ax.set(xlabel='x', ylabel='y', title='Plot')

            plt.show()

        def add_bar(self, x, y):
            """Add a bar graph to the map.

            Args:
                x (str, optional): Data to use for the x-axis.
                y (str, optional): Data to use for the y-axis.
                **kwargs: Other keyword arguments for ipywidgets.HTML().

            Returns:
                matplotlib.plot: Generates a bar graph. 
            """
            import matplotlib.pyplot as plt
            import numpy as np

            plt.style.use('_mpl-gallery')

            # plot
            fig, ax = plt.subplots()
            ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
            ax.set(xlabel='x', ylabel='y', title='Bar Graph')

            plt.show()

        def add_pie(self, x):
            """Add a pie chart to the map.

            Args:
                x (str, optional): Data to use for the pie chart.
                **kwargs: Other keyword arguments for ipywidgets.HTML().

            Returns:
                matplotlib.plot: Generates a pie graph. 
            """
            import matplotlib.pyplot as plt
            import numpy as np

            plt.style.use('_mpl-gallery-nogrid')

            # plot
            fig, ax = plt.subplots()
            ax.pie(x, radius=3, wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=True)
            ax.set(xlabel='x', title='Pie Chart')

            plt.show()


        def add_chart(self, position="bottomleft", **kwargs):
            """Add a figure to the map.

            Args:
                content (str | ipywidgets.Widget | object): The chart to add.
                position (str, optional): The position of the widget. Defaults to "bottomright".
                **kwargs: Other keyword arguments for ipywidgets.HTML().

            Returns:
                ipywidgets.chart: Adds a chart dropdown widget to map. 
            """
            import streamlit as st
            import ipywidgets as widgets

            allowed_positions = ["topleft", "topright", "bottomleft", "bottomright"]

            if position not in allowed_positions:
                raise Exception(f"position must be one of {allowed_positions}")

            chart_type = widgets.Dropdown(
                options=['PLOT','BAR','PIE'],
                value=None,
                description='Chart:',
                style={'description_width': 'initial'},
                layout=widgets.Layout(width='250px')
            )

            chart_ctrl = ipyleaflet.WidgetControl(widget=chart_type, position=position)
            self.add_control(chart_ctrl)
            
            def change_chart(change):
                if change['new']:
                    selected_option = chart_type.value
                    self.add_widget(selected_option, position=position)

            chart_type.observe(change_chart, names='value')



        def add_widget(self, content, position="bottomright", **kwargs):
            """Add a widget (e.g., text, HTML, figure) to the map.

            Args:
                content (str | ipywidgets.Widget | object): The widget to add.
                position (str, optional): The position of the widget. Defaults to "bottomright".
                **kwargs: Other keyword arguments for ipywidgets.HTML().

            Returns:
                ipyleaflet.WidgetControl: Adds a widget to the map. 
            """

            allowed_positions = ["topleft", "topright", "bottomleft", "bottomright"]

            if position not in allowed_positions:
                raise Exception(f"position must be one of {allowed_positions}")

            if "layout" not in kwargs:
                kwargs["layout"] = widgets.Layout(padding="0px 4px 0px 4px")
            try:
                if isinstance(content, str):
                    widget = widgets.HTML(value=content, **kwargs)
                    control = ipyleaflet.WidgetControl(widget=widget, position=position)
                else:
                    output = widgets.Output(**kwargs)
                    with output:
                        display(content)
                    control = ipyleaflet.WidgetControl(widget=output, position=position)
                self.add(control)

            except Exception as e:
                raise Exception(f"Error adding widget: {e}")


        def add_csv(self, in_csv, out_file, out_format, x="longitude", y="latitude"):
            import csv
            import geopandas as gpd
            from shapely.geometry import Point

            # Read CSV file and extract lat/lon coordinates
            points = []
            with open(in_csv, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    lon = float(row[x])
                    lat = float(row[y])
                    point = Point(lon, lat)
                    points.append(point)

            # Create a GeoDataFrame from the points
            gdf = gpd.GeoDataFrame(geometry=points)

            # Save GeoDataFrame to the specified output format
            if out_format == 'shapefile':
                gdf.to_file(out_file, driver='ESRI Shapefile')
            elif out_format == 'geojson':
                gdf.to_file(out_file, driver='GeoJSON')
            else:
                print("Unsupported output format. Please choose either 'shapefile' or 'geojson'.")

            #gj = gdf.__geo_interface__
            #self.add_csv(gj, out_file=out_file, out_format=out_format)



        def add_points_from_csv(self, in_csv, x="longitude", y="latitude", label=None, layer_name="Marker cluster"):

            import pandas as pd
            import folium
            from folium.plugins import MarkerCluster
            # Load CSV data into a pandas DataFrame
            df = pd.read_csv(in_csv)
            
            # Create a MarkerCluster layer
            marker_cluster = MarkerCluster(name=layer_name)
            
            
            # Iterate over rows and add markers to the cluster
            for index, row in df.iterrows():
                location = [row[y], row[x]]  # Swap x and y to match lat/lon
                marker = folium.Marker(location=location, popup=row[label] if label else None)
                marker.add_to(marker_cluster)
            
            #markercluster = 
            #self.add_points_from_csv(markercluster)


        def add_button(self, position = "topleft", **kwargs):
            import ipywidgets as widgets
            from IPython.display import display
            from ipyfilechooser import FileChooser

            allowed_positions = ["topleft", "topright", "bottomleft", "bottomright"]

            if position not in allowed_positions:
                raise Exception(f"position must be one of {allowed_positions}")
            
            button = widgets.Button(
                description='Create Marker Cluster',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Click me',
                icon='check' # (FontAwesome names without the `fa-` prefix)
            )
            
            marker_ctrl = ipyleaflet.WidgetControl(widget=button, position= "topleft")
            self.create_marker_cluster_tool(marker_ctrl)
            
            def create_marker_cluster(self):
                filepath = self.file_chooser.selected_path
                if filepath:
                    # Load CSV data into a pandas DataFrame
                    df = pd.read_csv(filepath)

                    # Create a MarkerCluster layer
                    marker_cluster = MarkerCluster(name="Marker cluster")

                    # Iterate over rows and add markers to the cluster
                    for index, row in df.iterrows():
                        location = [row["latitude"], row["longitude"]]
                        marker = folium.Marker(location=location)
                        marker.add_to(marker_cluster)







