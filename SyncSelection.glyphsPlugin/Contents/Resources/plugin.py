# encoding: utf-8

###########################################################################################################
#
#
#	General Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *

class SyncSelection(GeneralPlugin):
	def settings(self):
		self.name = Glyphs.localize({
			'en': u'Sync Layer Selections', 
			'de': u'Auswahl zwischen Ebenen synchronisieren',
			'es': u'Sincronizar selección de todas las capas',
			'fr': u'Synchroniser les sélections entre les calques',
		})
	
	def start(self):
		print "start"
		Glyphs.registerDefault("com.mekkablue.SyncSelection.state", False)

		menuItem = NSMenuItem(self.name, self.toggleSelectionSync)
		menuItem.setState_(bool(Glyphs.defaults["com.mekkablue.SyncSelection.state"]))
		Glyphs.menu[EDIT_MENU].append(menuItem)
		
		if Glyphs.defaults["com.mekkablue.SyncSelection.state"]:
			Glyphs.addCallback(self.keepSelectionInSync, UPDATEINTERFACE)
	
	def __del__(self):
		try:
			Glyphs.removeCallback(self.keepSelectionInSync, UPDATEINTERFACE)
		except:
			pass # exit gracefully
	
	def toggleSelectionSync(self, sender):
		if Glyphs.defaults["com.mekkablue.SyncSelection.state"]:
			Glyphs.defaults["com.mekkablue.SyncSelection.state"] = False
			Glyphs.removeCallback(self.keepSelectionInSync, UPDATEINTERFACE)
		else:
			Glyphs.defaults["com.mekkablue.SyncSelection.state"] = True
			Glyphs.addCallback(self.keepSelectionInSync, UPDATEINTERFACE)
			
		
		currentState = Glyphs.defaults["com.mekkablue.SyncSelection.state"]
		Glyphs.menu[EDIT_MENU].submenu().itemWithTitle_(self.name).setState_(currentState)
		
	
	def keepSelectionInSync(self, sender):
		# only sync when there is a document and a tab is open:
		if Glyphs.font and Glyphs.font.currentTab:
			
			# do not sync when Select All Layers tool is active:
			try:
				toolClass = Glyphs.currentDocument.windowController().toolEventHandler().className()
			except:
				toolClass = None
				
			if toolClass != "GlyphsToolSelectAllLayers":
				
				# only sync when a glyph layer is open for editing:
				layer = Glyphs.font.currentTab.activeLayer()
				if layer and layer.className() != "GSBackgroundLayer":
					glyph = layer.glyph()
					selection = layer.selection
					otherLayers = [l for l in glyph.layers if l != layer and l.compareString() == layer.compareString()]

					# reset selection in other layers:
					for otherLayer in otherLayers:
						otherLayer.selection = None

					# step through other layers and sync selection:
					if selection:
						if otherLayers:
						
							# sync anchors:
							for thisAnchor in layer.anchors:
								if thisAnchor in selection:
									for otherLayer in otherLayers:
										try:
											otherLayer.selection.append(otherLayer.anchors[thisAnchor.name])
										except:
											pass
					
							# sync node selection:
							for i,thisPath in enumerate(layer.paths):
								for j,thisNode in enumerate(thisPath.nodes):
									if thisNode in selection:
										for otherLayer in otherLayers:
											try:
												otherLayer.selection.append(otherLayer.paths[i].nodes[j])
											except:
												pass
						
							# sync selection of components:
							for i,thisComponent in enumerate(layer.components):
								if thisComponent in selection:
									for otherLayer in otherLayers:
										try:
											otherLayer.selection.append(otherLayer.components[i])
										except:
											pass
					
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	