# Defines custom queryset managers

from django.db import models
from django.db.models import Q

class SourceQuerySet(models.query.QuerySet):
	'''Manager of source methods and attributes via django-model-utils PassThroughManager'''
	def field_sort(self, letter, source_field):
		if source_field == 'author':
			return self.filter(author__last_name__startswith=letter).order_by('author__last_name')
		if source_field == 'title':
			return self.filter(title__startswith=letter).order_by('title')
		if source_field == 'city':
			return self.filter(publisher__city__startswith=letter).order_by('publisher__city')

	def get_library(self, library):
		'''
		Method to quickly retrieve the library-specific queryset
		like Source.objects.get_library('virtual')
		'''
		return self.filter(lib_type=library)

	def get_source(self, source):
		return self.filter(source_type=source)

	def count_sources(self):
		return self.all().count()

class PageQuerySet(models.query.QuerySet):
	'''Manager that generates customised querysets for getting pages'''

	def get_frontcover(self):
		return self.get(page_number__contains='frco').image

	def get_backcover(self):
		return self.get(page_number__contains='bco').image

	def get_singleimage(self, req_page):
		'''Get requested image'''
		return self.get(page_number__contains=req_page).image

	def get_coverimages(self):
		'''Returns queryset of the cover images'''
		coverimage_queryset = self.filter(
			Q(page_number__contains='frco') |
			Q(page_number__contains='tp') |
			Q(page_number__contains='info') |
			Q(page_number__contains='bco')
		)
		return coverimage_queryset

	def get_contentimages(self):
		'''Returns queryset of images excluding coverimages'''
		contentimage_queryset = self.exclude(
			Q(page_number__contains='frco') |
			Q(page_number__contains='tp') |
			Q(page_number__contains='info') |
			Q(page_number__contains='bco')
		)

		return contentimage_queryset

	def count_contentimages(self):
		return self.get_contentimages().count()

# the following is library-specific! #
	def order_by_actualpagenumber(self, queryset):
		'''
		As a SourcePage object's actual_pagenumber cannot be an IntegerField (some pages may include hyphens),
		a library-specific queryset ordering on actual_pagenumber is needed.
		This function forces a numerical order of a given queryset.
		'''
		return queryset.extra(
							select={'library_sourcepage_actual_pagenumber': "CONVERT(SUBSTRING_INDEX(actual_pagenumber,'-',1),UNSIGNED INTEGER)"}
							).order_by('library_sourcepage_actual_pagenumber')
# #

	def get_allsurroundingimages(self, req_page):
		'''
		Returns dictionary with a requested image objects and its neighbours

		!!! Includes the library-specific function order_by_actualpagenumber(); delete if not needed !!!

		'''
		chosen_image = self.get(page_number__contains=req_page)

		previous_images = []
		next_images = []
		chosen_index = None

		for index, item in enumerate(self.order_by_actualpagenumber(self.get_contentimages())):
			if item == chosen_image:
				chosen_index = index
			else:
				if chosen_index == None:
					previous_images.append(item)
				else:
					next_images.append(item)

		get_images = {
			'chosen_image': chosen_image,
			'previous_images': previous_images,
			'next_images': next_images,
			}

		return get_images

	def get_two_surroundingimages(self, req_page):
		'''
		Returns dictionary with 2 objects: previous and next image
		'''
		try:
			previous_image = self.filter(page_number__lt=req_page).reverse()[0]
		except IndexError:
			previous_image = ''

		try:
			next_image = self.filter(page_number__gt=req_page)[0]
		except IndexError:
			next_image = ''

		return {
				'previous_image': previous_image,
				'next_image': next_image
			}
