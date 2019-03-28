"""
This application loads data through subclasses of nmutils.core.Scan. 
These subclasses should have the option "dataType" for data loading,
and should expect the 'xrd' and 'xrf' values for this keyword. In 
addition, they can have whatever options they want.
"""

# hdf5plugin is needed to read compressed Eiger files, and has to be
# imported before h5py.
try:
    import hdf5plugin 
except ImportError:
    print "hdf5plugin not found - may not be able to read compressed Eiger files"

# silx automatically chooses PyQt version. You can force it here
# by first importing it explicitly.
# #from PyQt5 import QtCore

# make sure silx is not too old (API features have appeared)
from distutils.version import LooseVersion
try:
    import silx
    assert LooseVersion(silx.version) >= LooseVersion('0.10.1')
except:
    raise Exception('This application requires silx >= 0.10.1')

from silx.gui import qt
print 'silx %s using' % silx.version, qt.BINDING
from silx.gui.icons import getQIcon
import design
import sys
import gc
import numpy as np
from scipy.interpolate import griddata
import nmutils
import time

# using the single inheritance method here, as described here,
# http://pyqt.sourceforge.net/Docs/PyQt4/designer.html
#
# this means:
# 1) create a new class for the containing widget, which will 
#    have all the code and connections
# 2) create an UI object from qt-designer and own it as self.ui
# 3) run its setupUi method and pass the containing widget (self)
#
class ScanViewer(qt.QMainWindow):

    def __init__(self, filename=None):

        # Qt base class constructor
        super(ScanViewer, self).__init__()

        # instantiate the form class and set it up in the current QMainWindow
        self.ui = design.Ui_MainWindow()
        self.ui.setupUi(self)

        # possibly set initial values
        if filename:
            self.ui.filenameBox.setText(filename)

        # set up default plot settings
        self.diffCmap = {'name':'temperature', 'autoscale':True, 'normalization':'log'}
        self.mapCmap = {'name':'gray', 'autoscale':True, 'normalization':'linear'}

        # populate the scan class list
        self.ui.scanClassBox.addItem('select scan type')
        for subclass in nmutils.core.Scan.__subclasses__():
            self.ui.scanClassBox.addItem(subclass.__name__)
            for subclass_ in subclass.__subclasses__():
                self.ui.scanClassBox.addItem(subclass_.__name__)

        # connect browse button
        def wrap():
            result = qt.QFileDialog.getOpenFileName()
            # PyQt5 gives a tuple here...
            if type(result) == tuple:
                result = result[0]
            self.ui.filenameBox.setText(result)
        self.ui.browseButton.clicked.connect(wrap)

        # populate the options tab
        self.ui.scanClassBox.currentIndexChanged.connect(self.populateOptions)

        # connect load button
        self.ui.loadButton.clicked.connect(self.load)

        # dummy scan
        self.scan = None

    def _current_subclass_opts(self):
        subclass_ = str(self.ui.scanClassBox.currentText())
        try:
            subclass = getattr(nmutils.core, subclass_)
        except:
            return
        return subclass.default_opts.copy()

    def gatherOptions(self):
        # collect options from the options tab:
        opts = {}
        for name, w in self.formWidgets.iteritems():
            if isinstance(w, qt.QCheckBox):
                val = bool(w.isChecked())
            elif isinstance(w, qt.QComboBox):
                val = str(w.currentText())
            elif isinstance(w, qt.QLineEdit) and not w.evaluate_me:
                val = str(w.text())
            elif isinstance(w, qt.QLineEdit) and w.evaluate_me:
                val = eval(str(w.text()))
            else:
                val = w.value()
            opts[name] = val

        # collect special options from the top of the GUI:
        subclass_opts = self._current_subclass_opts()
        if 'path' in subclass_opts.keys():
            opts['path'] = str(self.ui.filenameBox.text())
        if 'fileName' in subclass_opts.keys():
            opts['fileName'] = str(self.ui.filenameBox.text())
        if 'scanNr' in subclass_opts.keys():
            opts['scanNr'] = self.ui.scanNumberBox.value()

        return opts

    def populateOptions(self):
        grid = self.ui.optionsGrid
        # remove all old options
        for i in reversed(range(grid.count())): 
            grid.itemAt(i).widget().setParent(None)

        # add new ones
        opts = self._current_subclass_opts()
        self.formWidgets = {}
        i = 0
        for name, opt in opts.iteritems():
            # special: the options scanNr and fileName (or path) have their input
            # widgets at the top of the GUI for convenience, while dataType is
            # used by the viewer. Handled below.
            if name in ('dataType', 'scanNr', 'path', 'fileName'):
                continue
            grid.addWidget(qt.QLabel(name), i, 0)
            grid.addWidget(qt.QLabel(opt['doc']), i, 2)
            if opt['type'] == int:
                w = qt.QSpinBox()
                w.setMaximum(9999)
                w.setValue(opt['value'])
            elif opt['type'] == float:
                w = qt.QDoubleSpinBox()
                w.setValue(opt['value'])
            elif opt['type'] == bool:
                w = qt.QCheckBox()
                w.setChecked(opt['value'])
            elif opt['type'] in (list, tuple):
                w = qt.QLineEdit()
                w.setText(str(opt['value']))
                w.evaluate_me = True
            elif type(opt['type']) in (list, tuple):
                w = qt.QComboBox()
                defaultindex = 0
                for j, item in enumerate(opt['type']):
                    w.addItem(item)
                    if item == opt['value']:
                        defaultindex = j
                w.setCurrentIndex(defaultindex)
            else:
                w = qt.QLineEdit()
                w.setText(opt['value'])
                w.evaluate_me = False
            grid.addWidget(w, i, 1)
            # save a dict of the options widgets, to parse when loading
            self.formWidgets[name] = w
            i += 1

        # special treatment
        oldtext = str(self.ui.filenameBox.text())
        if 'path' in opts.keys() and oldtext.startswith('<'):
            self.ui.filenameBox.setText('<data path>')
        elif 'fileName' in opts.keys() and oldtext.startswith('<'):
            self.ui.filenameBox.setText('<input file>')
        self.ui.filenameBox.setDisabled(not ('path' in opts.keys() or 'fileName' in opts.keys()))
        self.ui.browseButton.setDisabled(not ('path' in opts.keys() or 'fileName' in opts.keys()))
        self.ui.scanNumberBox.setDisabled('scanNr' not in opts.keys())

    def statusOutput(self, msg):
        self.ui.statusbar.showMessage(msg)
        self.ui.statusbar.showMessage(msg)

    def load(self):
        try:
            self.statusOutput("Loading data...")
            if self.scan and not self.ui.appendBox.isChecked():
                print "Deleting previous scan from memory"
                # These references have to go
                self.ui.comWidget.setScan(None)
                self.ui.xrdWidget.setScan(None)
                self.ui.xrfWidget.setScan(None)
                del(self.scan)
                self.scan = None
                # enforcing garbage collection for good measure
                gc.collect()

            # construct a scan
            try:
                subclass = str(self.ui.scanClassBox.currentText())
                scan_ = getattr(nmutils.core, subclass)()
            except:
                raise Exception("Invalid subclass")

            # get options
            opts = self.gatherOptions()

            # add xrd data:
            try:
                scan_.addData(dataType='xrd', name='xrd', **opts)
                print "loaded xrd data: %d positions, %d x %d pixels"%(scan_.data['xrd'].shape)
                has_xrd = True
            except MemoryError:
                print "Out of memory! Consider cropping or binning your images"
                has_xrd = False
            except AttributeError:
                print "no xrd data found"
                has_xrd = False

            # add xrf data:
            try:
                scan_.addData(dataType='xrf', name='xrf', **opts)
                print "loaded xrf data: %d positions, %d channels"%(scan_.data['xrf'].shape)
                has_xrf = True
            except AttributeError:
                print "no xrf data found"
                has_xrf = False

            # append or store loaded scan as it is
            if not self.scan:
                self.scan = scan_
            else:
                self.scan.merge(scan_)

            # update the widgets
            if self.scan.nPositions > 1:
                if has_xrd:
                    self.ui.comWidget.setScan(self.scan)
                    self.ui.xrdWidget.setScan(self.scan)
                if has_xrf:
                    self.ui.xrfWidget.setScan(self.scan)
            self.statusOutput("")
        except Exception as e:
            self.statusOutput("Loading failed. See terminal output for details.")
            print 'The error was: ', e

if __name__ == '__main__':
    # you always need a qt app
    app = qt.QApplication(sys.argv)
    # for convenience, you can pass the filename as an argument
    fn = None
    if len(sys.argv) >= 2:
        fn = sys.argv[1]
    # instantiate and show the main object
    viewer = ScanViewer(fn)
    viewer.show()
    # run the app
    app.exec_()

