import json
import glob
from pysph.solver.utils import load, get_files
from IPython.display import display, clear_output, Image
import ipywidgets as widgets


class Viewer(object):

    '''
    Example
    -------

    >>> from pysph.solver.utils import ipython
    >>> sample = ipython.Viewer2D('/home/uname/pysph_files/dam_Break_2d_output')
    >>> sample.interactive_plot()
    >>> sample.show_log()
    >>> sample.show_info()
    '''

    def __init__(self, path, cache=True):

        # Configuring the path #

        self.path = path
        self.paths_list = get_files(path)

        # Caching #
        # Note : Caching is only used by get_frame and widget handlers.
        if cache:
            self.cache = {}
        else:
            self.cache = None

    def get_frame(self, frame):
        '''Return particle arrays for a given frame number with caching.


        Parameters
        ----------

        frame : int

        Returns
        -------

        A dictionary.

        Examples
        --------

        >>> sample = Viewer2D('/home/deep/pysph/trivial_inlet_outlet_output/')
        >>> sample.get_frame(12)
        {'arrays': {'fluid': <pysph.base.particle_array.ParticleArray at 0x7f3f7d144d60>,
        'inlet': <pysph.base.particle_array.ParticleArray at 0x7f3f7d144b98>,
        'outlet': <pysph.base.particle_array.ParticleArray at 0x7f3f7d144c30>},
        'solver_data': {'count': 240, 'dt': 0.01, 't': 2.399999999999993}}


        '''

        if self.cache is not None:
            if frame in self.cache:
                temp_data = self.cache[frame]
            else:
                self.cache[frame] = temp_data = load(self.paths_list[frame])
        else:
            temp_data = load(self.paths_list[frame])

        return temp_data

    def show_log(self):
        '''
        Prints the content of log file.
        '''

        print("Printing log : \n\n")
        path = self.path + "*.log"
        with open(glob.glob(path)[0], 'r') as logfile:
            for lines in logfile:
                print(lines)

    def show_results(self):
        '''
        Show if there are any png, jpeg, jpg, or bmp images.
        '''

        imgs = tuple()
        for extension in ['png', 'jpg', 'jpeg', 'bmp']:
            temppath = self.path + "*." + extension
            for paths in glob.glob(temppath):
                imgs += (Image(paths),)
        if len(imgs) != 0:
            display(*imgs)
        else:
            print("No results to show.")

    def show_info(self):
        '''
        Print contents of the .info file present in the output directory,
        keys present in results.npz,  number of files and
        information about paricle arrays.
        '''

        # General Info #

        path = self.path + "*.info"
        with open(glob.glob(path)[0], 'r') as infofile:
            data = json.load(infofile)

            print('Printing info : \n')
            for key in data.keys():
                if key == 'cpu_time':
                    print(key + " : " + str(data[key]) + " seconds")
                else:
                    print(key + " : " + str(data[key]))

            print('Number of files : {}'.format(len(self.paths_list)))

        # Particle Info #

        temp_data = load(self.paths_list[0])['arrays']

        for key in temp_data:
            print("  {} :".format(key))
            print("    Number of particles : {}".format(
                temp_data[key].get_number_of_particles())
            )
            print("    Output Property Arrays : {}".format(
                temp_data[key].output_property_arrays)
            )

        # keys in results.npz

        from numpy import load as npl

        path = self.path + "*results*"
        files = glob.glob(path)
        if len(files) != 0:
            data = npl(files[0])
            print("\nKeys in results.npz :")
            print(data.keys())

    def show_all(self):
        self.show_info()
        self.show_results()
        self.show_log()


class Viewer2DWidgets(object):

    def __init__(self, file, file_count, handlers):

        temp_data = load(file)['arrays']

        self.frame = widgets.IntSlider(
            min=0,
            max=file_count,
            step=1,
            value=0,
            description='frame',
            layout=widgets.Layout(width='600px'),
        )
        self.frame.observe(handlers['frame'], 'value')

        self.save_figure = widgets.Text(
                value='',
                placeholder='example.pdf',
                description='Save figure',
                disabled=False,
                layout=widgets.Layout(width='240px', display='flex')
        )
        self.save_figure.on_submit(handlers['save_figure'])

        self.particles = {}

        class extend(object):
            pass

        for particles_type in temp_data.keys():

            self.particles[particles_type] = extend()

            self.particles[particles_type].scalar = widgets.Dropdown(
                options=[
                    'None'
                ]+temp_data[particles_type].output_property_arrays,
                value='rho',
                description="scalar",
                disabled=False,
                layout=widgets.Layout(width='240px', display='flex')
            )
            self.particles[particles_type].scalar.owner = particles_type
            self.particles[particles_type].scalar.observe(
                handlers['scalar_handler'],
                'value',
            )

            self.particles[particles_type].legend = widgets.ToggleButton(
                value=False,
                description="legend",
                disabled=False,
                tooltip='Description',
                layout=widgets.Layout(width='80px', display='flex')
            )
            self.particles[particles_type].legend.owner = particles_type

            self.particles[particles_type].legend.observe(
                handlers['legend_handler'],
                'value',
            )

            self.particles[particles_type].vector = widgets.Text(
                value='',
                placeholder='variable1,variable2',
                description='vector',
                disabled=False,
                layout=widgets.Layout(width='240px', display='flex')
            )

            self.particles[particles_type].vector.owner = particles_type
            self.particles[particles_type].vector.observe(
                handlers['vector_handler'],
                'value',
            )

            self.particles[particles_type].vector_width = widgets.FloatSlider(
                min=1,
                max=100,
                step=1,
                value=25,
                description='vector width',
                layout=widgets.Layout(width='300px'),
            )
            self.particles[particles_type].vector_width.owner = particles_type

            self.particles[particles_type].vector_width.observe(
                handlers['vector_width_handler'],
                'value',
            )

            self.particles[particles_type].vector_scale = widgets.FloatSlider(
                min=1,
                max=100,
                step=1,
                value=55,
                description='vector scale',
                layout=widgets.Layout(width='300px'),
            )
            self.particles[particles_type].vector_scale.owner = particles_type
            self.particles[particles_type].vector_scale.observe(
                handlers['vector_scale_handler'],
                'value',
            )

            self.particles[particles_type].scalar_size = widgets.FloatSlider(
                min=0,
                max=50,
                step=1,
                value=10,
                description='scalar size',
                layout=widgets.Layout(width='300px'),
            )
            self.particles[particles_type].scalar_size.owner = particles_type
            self.particles[particles_type].scalar_size.observe(
                handlers['scalar_size_handler'],
                'value',
            )


class Viewer2D(Viewer):

    '''
    Example
    -------

    >>> from pysph.solver.utils import ipython
    >>> sample = ipython.Viewer2D('/home/uname/pysph_files/dam_Break_2d_output')
    >>> sample.interactive_plot()
    >>> sample.show_log()
    >>> sample.show_info()
    '''

    def _create_widgets(self):

        handlers = {}
        handlers['frame'] = self._frame_handler
        handlers['scalar_handler'] = self._scalar_handler
        handlers['vector_handler'] = self._vector_handler
        handlers['vector_scale_handler'] = self._vector_scale_handler
        handlers['vector_width_handler'] = self._vector_width_handler
        handlers['scalar_size_handler'] = self._scalar_size_handler
        handlers['save_figure'] = self._save_figure_handler
        handlers['legend_handler'] = self._legend_handler

        self._widgets = Viewer2DWidgets(
            file=self.paths_list[0],
            file_count=len(self.paths_list) - 1,
            handlers=handlers
        )

    def _display_widgets(self):
        '''
        Display the widgets created using _create_widgets() method.
        '''

        from ipywidgets import HBox, VBox, Label, Layout

        items = []
        for particles_type in self._widgets.particles.keys():
            items.append(
                VBox([
                    Label(particles_type),
                    self._widgets.particles[particles_type].scalar,
                    self._widgets.particles[particles_type].vector,
                    self._widgets.particles[particles_type].vector_scale,
                    self._widgets.particles[particles_type].vector_width,
                    self._widgets.particles[particles_type].scalar_size,
                    self._widgets.particles[particles_type].legend,

                ],
                    layout=Layout(display='flex'))
            )

        display(
            VBox(
                [
                    HBox(items, layout=Layout(display='flex')),
                    self._widgets.frame,
                    self._widgets.save_figure
                ]
            )
        )

    def _configure_plot(self):
        '''
        Set attributes for plotting.
        '''

        from matplotlib import pyplot as plt

        self.figure = plt.figure()
        self._scatter_ax = self.figure.add_axes([0, 0, 1, 1])
        self._scatters = {}
        self._cbar_ax = {}
        self._cbars = {}
        self._vectors = {}

    def interactive_plot(self):
        '''
        Set plotting attributes, create widgets and display them
        along with the interactive plot.

        Use %matplotlib notebook for more interactivity.
        '''

        self._configure_plot()
        self._create_widgets()
        self._frame_handler(None)
        self._display_widgets()

    def _frame_handler(self, change):

        temp_data = self.get_frame(self._widgets.frame.value)

        # scalars #

        self.figure.set_label(
            "Time : " + str(temp_data['solver_data']['t'])
        )
        temp_data = temp_data['arrays']

        for sct in self._scatters.values():
            if sct in self._scatter_ax.collections:
                self._scatter_ax.collections.remove(sct)

        self._scatters = {}
        for particles_type in self._widgets.particles.keys():
            if self._widgets.particles[particles_type].scalar.value != 'None':
                self._scatters[particles_type] = self._scatter_ax.scatter(
                    temp_data[particles_type].x,
                    temp_data[particles_type].y,
                    c=getattr(
                            temp_data[particles_type],
                            self._widgets.particles[
                                particles_type
                            ].scalar.value
                    ),
                    s=self._widgets.particles[
                        particles_type
                    ].scalar_size.value,
                )
        self._legend_handler(None, manual=True)

        # _vectors #

        for vct in self._vectors.values():
            if vct in self._scatter_ax.collections:
                self._scatter_ax.collections.remove(vct)

        self._vectors = {}
        for particles_type in self._widgets.particles.keys():
            if self._widgets.particles[particles_type].vector.value != '':
                self._vectors[particles_type] = self._scatter_ax.quiver(
                    temp_data[particles_type].x,
                    temp_data[particles_type].y,
                    getattr(
                        temp_data[particles_type],
                        self.self._widgets.particles[
                            particles_type
                        ].vector.value.split(",")[0]
                    ),
                    getattr(
                        temp_data[particles_type],
                        self._widgets.particles[
                            particles_type
                        ].vector.value.split(",")[1]
                    ),
                    ((getattr(
                        temp_data[particles_type],
                        self._widgets.particles[
                            particles_type
                        ].vector.value.split(",")[0]
                    ))**2 + (getattr(
                        temp_data[particles_type],
                        self._widgets.particles[
                            particles_type
                        ].vector.value.split(",")[1]
                        ))**2
                    )**0.5,
                    scale=self._widgets.particles[
                        particles_type
                    ].vector_scale.value,
                    width=(self._widgets.particles[
                        particles_type
                    ].vector_width.value)/10000,
                )

        # show the changes #
        clear_output(wait=True)
        display(self.figure)

    def _scalar_handler(self, change):

        temp_data = self.get_frame(self._widgets.frame.value)['arrays']

        particles_type = change['owner'].owner

        if particles_type in self._scatters.keys():
            if self._scatters[particles_type] in self._scatter_ax.collections:
                self._scatter_ax.collections.remove(
                    self._scatters[particles_type]
                )

        if change['new'] != 'None':
            self._scatters[particles_type] = self._scatter_ax.scatter(
                temp_data[particles_type].x,
                temp_data[particles_type].y,
                c=getattr(temp_data[particles_type], change['new']),
                s=self._widgets.particles[particles_type].scalar_size.value
            )

        self._legend_handler(None, manual=True)
        clear_output(wait=True)
        display(self.figure)

    def _vector_handler(self, change):
        '''
        Bug : Arrows go out of the figure
        '''

        temp_data = self.get_frame(
            self._widgets.frame.value
        )['arrays']

        particles_type = change['owner'].owner

        if particles_type in self._vectors.keys():
            if self._vectors[particles_type] in self._scatter_ax.collections:
                self._scatter_ax.collections.remove(
                    self._vectors[particles_type]
                )

        if change['new'] != '':
            self._vectors[particles_type] = self._scatter_ax.quiver(
                temp_data[particles_type].x,
                temp_data[particles_type].y,
                getattr(
                    temp_data[particles_type],
                    change['new'].split(",")[0]
                ),
                getattr(
                    temp_data[particles_type],
                    change['new'].split(",")[1]
                ),
                ((getattr(
                    temp_data[particles_type],
                    change['new'].split(",")[0]
                ))**2 + (getattr(
                    temp_data[particles_type], change['new'].split(",")[1]
                ))**2
                )**0.5,
                scale=self._widgets.particles[
                    particles_type
                ].vector_scale.value,
                width=(self._widgets.particles[
                    particles_type
                ].vector_width.value)/10000,
            )

        clear_output(wait=True)
        display(self.figure)

    def _vector_scale_handler(self, change):
        # the widget value must already have updated.
        particles_type = change['owner'].owner
        if particles_type in self._vectors.keys():
            self._vectors[particles_type].scale = change['new']
        clear_output(wait=True)
        display(self.figure)

    def _scalar_size_handler(self, change):
        particles_type = change['owner'].owner
        if particles_type in self._scatters.keys():
            self._scatters[particles_type].set_sizes([change['new']])
        clear_output(wait=True)
        display(self.figure)

    def _vector_width_handler(self, change):
        # the widget value must already have updated.
        particles_type = change['owner'].owner
        if particles_type in self._vectors.keys():
            self._vectors[particles_type].width = change['new']/10000
        clear_output(wait=True)
        display(self.figure)

    def _legend_handler(self, change, manual=False):

        for _cbar_ax in self._cbar_ax.values():
            self.figure.delaxes(_cbar_ax)
        self._cbar_ax = {}
        self._cbars = {}
        self._scatter_ax.set_position([0, 0, 1, 1])
        for particles_type in self._widgets.particles.keys():
            if self._widgets.particles[particles_type].legend.value:
                if self._widgets.particles[
                    particles_type
                ].scalar.value != 'None':
                    self._scatter_ax.set_position(
                        [0, 0, 0.84 - 0.15*len(self._cbars.keys()), 1]
                    )
                    self._cbar_ax[particles_type] = self.figure.add_axes(
                            [
                                0.85 - 0.15*len(self._cbars.keys()),
                                0.02,
                                0.02,
                                0.82
                            ]
                    )
                    self._cbars[particles_type] = self.figure.colorbar(
                            self._scatters[particles_type],
                            cax=self._cbar_ax[particles_type]
                    )
                    self._cbars[particles_type].set_label(
                            particles_type + " : " +
                            self._widgets.particles[
                                particles_type
                            ].scalar.value
                    )
        if not manual:
            clear_output(wait=True)
            display(self.figure)

    def _save_figure_handler(self, change):

        for extension in [
            '.eps', '.pdf', '.pgf',
            '.png', '.ps', '.raw',
            '.rgba', '.svg', '.svgz'
        ]:
            if self._widgets.save_figure.value.endswith(extension):
                self.figure.savefig(self._widgets.save_figure.value)
                print(
                    "Saved figure as {} in the present working directory"
                    .format(
                        self._widgets.save_figure.value
                    )
                )
                break
        self._widgets.save_figure.value = ""
