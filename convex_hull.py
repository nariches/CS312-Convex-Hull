from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = True

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

##########################################
	def get_halves(self, points):
		halfIndex = len(points) // 2
		leftPoints = points[:halfIndex]
		rightPoints = points[halfIndex:]
		return leftPoints, rightPoints

	def get_slope(self, leftPoint, rightPoint):
		slope = (rightPoint.y() - leftPoint.y()) / (rightPoint.x() - leftPoint.x())
		return slope

	def increase_left_tan(self, leftHull, upperLeft, upperRight, iter):
		currSlope = self.get_slope(upperLeft, upperRight)
		newSlope = currSlope
		if (iter < len(leftHull)):
			newSlope = self.get_slope(leftHull[-iter], upperRight)
		if (newSlope < currSlope):
			return leftHull[-iter]
		else:
			return upperLeft

	def increase_right_tan(self, upperLeft, rightHull, upperRight, iter):
		currSlope = self.get_slope(upperLeft, upperRight)
		newSlope = currSlope
		if (iter < len(rightHull)):
			newSlope = self.get_slope(upperLeft, rightHull[iter])
		if (newSlope > currSlope):
			return rightHull[iter]
		else:
			return upperRight

	def decrease_left_tan(self, leftHull, lowerLeft, lowerRight, iter):
		currSlope = self.get_slope(lowerLeft, lowerRight)
		newSlope = currSlope
		if (iter < len(leftHull)):
			newSlope = self.get_slope(leftHull[iter], lowerRight)
		if (newSlope > currSlope):
			return leftHull[iter]
		else:
			return lowerLeft

	def decrease_right_tan(self, lowerLeft, rightHull, lowerRight, iter):
		currSlope = self.get_slope(lowerLeft, lowerRight)
		newSlope = currSlope
		if (iter < len(rightHull)):
			newSlope = self.get_slope(lowerLeft, rightHull[-iter])
		if (newSlope < currSlope):
			return rightHull[iter]
		else:
			return lowerRight

	def find_upper_tangent(self, leftHull, rightHull):
		rightmostFromLeft = leftHull[0]
		for i in range(len(leftHull)):
			if leftHull[i].x() > rightmostFromLeft.x():
				rightmostFromLeft = leftHull[i]
		leftmostFromRight = rightHull[0]
		upperLeft = rightmostFromLeft
		upperRight = leftmostFromRight
		i = 1
		while True:
			prevUpperLeft = upperLeft
			prevUpperRight = upperRight
			upperLeft = self.increase_left_tan(leftHull, upperLeft, upperRight, i)
			upperRight = self.increase_right_tan(upperLeft, rightHull, upperRight, i)
			if (prevUpperLeft == upperLeft and prevUpperRight == upperRight):
				break
			i += 1
		UpTanLine = QLineF(upperLeft, upperRight)
		self.blinkTangent([UpTanLine], BLUE)
		return upperLeft, upperRight

	def find_lower_tangent(self, leftHull, rightHull):
		rightmostFromLeft = leftHull[0]
		for i in range(len(leftHull)):
			if leftHull[i].x() > rightmostFromLeft.x():
				rightmostFromLeft = leftHull[i]
		leftmostFromRight = rightHull[0]
		lowerLeft = rightmostFromLeft
		lowerRight = leftmostFromRight
		i = 1
		while True:
			prevLowerLeft = lowerLeft
			prevLowerRight = lowerRight
			lowerLeft = self.decrease_left_tan(leftHull, lowerLeft, lowerRight, i)
			lowerRight = self.decrease_right_tan(lowerLeft, rightHull, lowerRight, i)
			if (prevLowerLeft == lowerLeft and prevLowerRight == lowerRight):
				break
			i += 1
		BotTanLine = QLineF(lowerLeft, lowerRight)
		self.blinkTangent([BotTanLine], GREEN)
		return lowerLeft, lowerRight


	def merge_hulls(self, leftHull, rightHull):
		upperLeftTan, upperRightTan = self.find_upper_tangent(leftHull, rightHull)
		lowerLeftTan, lowerRightTan = self.find_lower_tangent(leftHull, rightHull)
		mergedHull = []
		for i in range(len(leftHull)):
			if leftHull[i] == upperLeftTan:
				mergedHull.append(upperLeftTan)
				break
			mergedHull.append(leftHull[i])

		for i in range(len(rightHull)):
			if rightHull[i] == upperRightTan:
				for j in range(i, len(rightHull)):
					if rightHull[j] == lowerRightTan:
						mergedHull.append(lowerRightTan)
						break
					mergedHull.append(rightHull[j])
				break
		if leftHull[0] != lowerLeftTan:
			for i in range(len(leftHull)):
				if leftHull[i] == lowerLeftTan:
					for j in range(i, len(leftHull)):
						mergedHull.append(leftHull[j])

		return mergedHull



	def divide(self, points):
		if (len(points) < 3):
			return points
		leftPoints, rightPoints = self.get_halves(points)

		leftPoints = self.divide(leftPoints)
		rightPoints = self.divide(rightPoints)

		hull = self.merge_hulls(leftPoints, rightPoints)
		showHull = [QLineF(hull[i],hull[(i+1)%len(hull)]) for i in range(len(hull))]
		self.showHull(showHull, GREEN)
		return hull







# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )



		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		pointsXVal = sorted(points, key=lambda point:point.x())

		t2 = time.time()

		t3 = time.time()

		#polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3Z)]
		hull_points = self.divide(pointsXVal)  # REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		polygon = [QLineF(hull_points[i],hull_points[(i+1)%len(hull_points)]) for i in range(len(hull_points))]
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
