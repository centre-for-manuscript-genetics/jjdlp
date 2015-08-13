from haystack.utils import Highlighter
from django.utils.html import strip_tags

class NoTruncateHighlighter(Highlighter):
	'''Overrides Haystack Highlighter to force no truncate at the beginning'''
	def highlight(self, text_block):
		self.text_block = strip_tags(text_block)
		highlight_locations = self.find_highlightable_words()
		start_offset, end_offset = self.find_window(highlight_locations)

		# Change made:
		start_offset = 0

		return self.render_html(highlight_locations, start_offset, end_offset)