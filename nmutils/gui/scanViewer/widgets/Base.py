from silx.gui.plot import PlotWindow
from silx.gui.plot.Profile import ProfileToolBar
from silx.gui.icons import getQIcon
from silx.gui import qt
import numpy as np

class CustomPlotWindow(PlotWindow):
    """
    PlotWindow with the data display on.
    """
    def __init__(self, parent=None, **kwargs):
        # List of information to display at the bottom of the plot
        posInfo = [
            ('X', lambda x, y: x),
            ('Y', lambda x, y: y),
            ('Data', self._getActiveImageValue)]

        super(CustomPlotWindow, self).__init__(parent=parent, position=posInfo, **kwargs)

    def _getActiveImageValue(self, x, y):
        """Get value of active image at position (x, y)

        :param float x: X position in plot coordinates
        :param float y: Y position in plot coordinates
        :return: The value at that point or '-'
        """
        image = self.getActiveImage()
        if image is not None:
            data, params = image[0], image[4]
            ox, oy = params['origin']
            sx, sy = params['scale']
            if (y - oy) >= 0 and (x - ox) >= 0:
                # Test positive before cast otherwisr issue with int(-0.5) = 0
                row = int((y - oy) // sy)
                col = int((x - ox) // sx)
                if (row < data.shape[0] and col < data.shape[1]):
                    return data[row, col]
        return '-'

class PairedWidgetBase(qt.QWidget):
    """
    Base class for XrdWidget, XrfWidget and ScalarWidget. More should
    probably be moved here.
    """
    
    def togglePositions(self):
        if self.map.positionsAction.isChecked():
            self.map.addCurve(self.scan.positions[:,0], self.scan.positions[:,1], 
                legend='scan positions', symbol='+', color='red', linestyle=' ',
                resetzoom=False, replace=False)
        else:
            self.map.addCurve([], [], legend='scan positions', resetzoom=False, replace=False)

    def indexMarkerOn(self, on):
        if on:
            self.map.addCurve([self.scan.positions[self.selected_idx, 0]], 
                [self.scan.positions[self.selected_idx, 1]], symbol='o', color='red', 
                linestyle=' ', legend='index marker', resetzoom=False,
                replace=False)
        else:
            self.map.addCurve([], [], legend='index marker', 
                resetzoom=False, replace=False)

    def selectByIndex(self, idx):
        self.selectionMode = 'ind'
        self.selected_idx = idx
        self.indexMarkerOn(True)
        # clearing the mask also invokes self.updateImage():
        self.map.getMaskToolsDockWidget().widget().resetSelectionMask()
        self.selectionMode = 'roi'

    def selectByPosition(self, x, y):
        idx = np.argmin(np.linalg.norm(self.scan.positions - np.array((x, y)), axis=1))
        self.map.indexBox.setValue(idx)

    def clearSelection(self):
        # This does everything
        self.map.getMaskToolsDockWidget().widget().resetSelectionMask()
