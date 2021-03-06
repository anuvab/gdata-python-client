#!/usr/bin/python
#
# Copyright (C) 2006 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'j.s@google.com (Jeff Scudder)'


import unittest
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata
import atom
from gdata import test_data
import gdata.test_config as conf


class StartIndexTest(unittest.TestCase):
  
  def setUp(self):
    self.start_index = gdata.StartIndex()
    
  def testToAndFromString(self):
    self.start_index.text = '1'
    self.assertTrue(self.start_index.text == '1')
    new_start_index = gdata.StartIndexFromString(self.start_index.ToString())
    self.assertTrue(self.start_index.text == new_start_index.text)
    
    
class ItemsPerPageTest(unittest.TestCase):
  
  def setUp(self):
    self.items_per_page = gdata.ItemsPerPage()
    
  def testToAndFromString(self):
    self.items_per_page.text = '10'
    self.assertTrue(self.items_per_page.text == '10')
    new_items_per_page = gdata.ItemsPerPageFromString(
         self.items_per_page.ToString())
    self.assertTrue(self.items_per_page.text == new_items_per_page.text)


class GDataEntryTest(unittest.TestCase):

  def testIdShouldBeCleaned(self):
    entry = gdata.GDataEntryFromString(test_data.XML_ENTRY_1)
    element_tree = ElementTree.fromstring(test_data.XML_ENTRY_1)
    self.assertTrue(element_tree.findall(
        '{http://www.w3.org/2005/Atom}id')[0].text != entry.id.text)
    self.assertTrue(entry.id.text == 'http://www.google.com/test/id/url')
    
  def testGeneratorShouldBeCleaned(self):
    feed = gdata.GDataFeedFromString(test_data.GBASE_FEED)
    element_tree = ElementTree.fromstring(test_data.GBASE_FEED)
    self.assertTrue(element_tree.findall('{http://www.w3.org/2005/Atom}generator'
        )[0].text != feed.generator.text)
    self.assertTrue(feed.generator.text == 'GoogleBase')

  def testAllowsEmptyId(self):
    entry = gdata.GDataEntry()
    try:
      entry.id = atom.Id()
    except AttributeError:
      self.fail('Empty id should not raise an attribute error.')


class LinkFinderTest(unittest.TestCase):
  
  def setUp(self):
    self.entry = gdata.GDataEntryFromString(test_data.XML_ENTRY_1)

  def testLinkFinderGetsLicenseLink(self):
    self.assertEqual(isinstance(self.entry.GetLicenseLink(), atom.Link), 
                      True)
    self.assertEqual(self.entry.GetLicenseLink().href, 
        'http://creativecommons.org/licenses/by-nc/2.5/rdf')
    self.assertEqual(self.entry.GetLicenseLink().rel, 'license')

  def testLinkFinderGetsAlternateLink(self):
    self.assertEqual(isinstance(self.entry.GetAlternateLink(), atom.Link), 
                                 True)
    self.assertEqual(self.entry.GetAlternateLink().href, 
        'http://www.provider-host.com/123456789')
    self.assertEqual(self.entry.GetAlternateLink().rel, 'alternate')


class GDataFeedTest(unittest.TestCase):

  def testCorrectConversionToElementTree(self):
    test_feed = gdata.GDataFeedFromString(test_data.GBASE_FEED)
    self.assertTrue(test_feed.total_results is not None)
    element_tree = test_feed._ToElementTree()
    feed = element_tree.find('{http://www.w3.org/2005/Atom}feed')
    self.assertTrue(element_tree.find(
        '{http://a9.com/-/spec/opensearchrss/1.0/}totalResults') is not None)

  def testAllowsEmptyId(self):
    feed = gdata.GDataFeed()
    try:
      feed.id = atom.Id()
    except AttributeError:
      self.fail('Empty id should not raise an attribute error.')


class BatchEntryTest(unittest.TestCase):

  def testCorrectConversionFromAndToString(self):
    batch_entry = gdata.BatchEntryFromString(test_data.BATCH_ENTRY)
    
    self.assertEqual(batch_entry.batch_id.text, 'itemB')
    self.assertEqual(batch_entry.id.text, 
                      'http://www.google.com/base/feeds/items/'
                      '2173859253842813008')
    self.assertEqual(batch_entry.batch_operation.type, 'insert')
    self.assertEqual(batch_entry.batch_status.code, '201')
    self.assertEqual(batch_entry.batch_status.reason, 'Created')
    
    new_entry = gdata.BatchEntryFromString(str(batch_entry))

    self.assertEqual(batch_entry.batch_id.text, new_entry.batch_id.text)
    self.assertEqual(batch_entry.id.text, new_entry.id.text)
    self.assertEqual(batch_entry.batch_operation.type, 
                      new_entry.batch_operation.type)
    self.assertEqual(batch_entry.batch_status.code, 
                      new_entry.batch_status.code)
    self.assertEqual(batch_entry.batch_status.reason, 
                      new_entry.batch_status.reason)


class BatchFeedTest(unittest.TestCase):

  def setUp(self):
    self.batch_feed = gdata.BatchFeed()
    self.example_entry = gdata.BatchEntry(
        atom_id=atom.Id(text='http://example.com/1'), text='This is a test')

  def testConvertRequestFeed(self):
    batch_feed = gdata.BatchFeedFromString(test_data.BATCH_FEED_REQUEST)

    self.assertEqual(len(batch_feed.entry), 4)
    for entry in batch_feed.entry:
      self.assertTrue(isinstance(entry, gdata.BatchEntry))
    self.assertEqual(batch_feed.title.text, 'My Batch Feed')

    new_feed = gdata.BatchFeedFromString(str(batch_feed))

    self.assertEqual(len(new_feed.entry), 4)
    for entry in new_feed.entry:
      self.assertTrue(isinstance(entry, gdata.BatchEntry))
    self.assertEqual(new_feed.title.text, 'My Batch Feed')

  def testConvertResultFeed(self):
    batch_feed = gdata.BatchFeedFromString(test_data.BATCH_FEED_RESULT)
    
    self.assertEqual(len(batch_feed.entry), 4)
    for entry in batch_feed.entry:
      self.assertTrue(isinstance(entry, gdata.BatchEntry))
      if entry.id.text == ('http://www.google.com/base/feeds/items/'
                           '2173859253842813008'):
        self.assertEqual(entry.batch_operation.type, 'insert')
        self.assertEqual(entry.batch_id.text, 'itemB')
        self.assertEqual(entry.batch_status.code, '201')
        self.assertEqual(entry.batch_status.reason, 'Created')
    self.assertEqual(batch_feed.title.text, 'My Batch')

    new_feed = gdata.BatchFeedFromString(str(batch_feed))
    
    self.assertEqual(len(new_feed.entry), 4)
    for entry in new_feed.entry:
      self.assertTrue(isinstance(entry, gdata.BatchEntry))
      if entry.id.text == ('http://www.google.com/base/feeds/items/'
                           '2173859253842813008'):
        self.assertEqual(entry.batch_operation.type, 'insert')
        self.assertEqual(entry.batch_id.text, 'itemB')
        self.assertEqual(entry.batch_status.code, '201')
        self.assertEqual(entry.batch_status.reason, 'Created')
    self.assertEqual(new_feed.title.text, 'My Batch')

  def testAddBatchEntry(self):
    try:
      self.batch_feed.AddBatchEntry(batch_id_string='a')
      self.fail('AddBatchEntry with neither entry or URL should raise Error')
    except gdata.MissingRequiredParameters:
      pass

    new_entry = self.batch_feed.AddBatchEntry(
        id_url_string='http://example.com/1')
    self.assertEqual(len(self.batch_feed.entry), 1)
    self.assertEqual(self.batch_feed.entry[0].id.text, 
                      'http://example.com/1')
    self.assertEqual(self.batch_feed.entry[0].batch_id.text, '0')
    self.assertEqual(new_entry.id.text, 'http://example.com/1')
    self.assertEqual(new_entry.batch_id.text, '0')

    to_add = gdata.BatchEntry(atom_id=atom.Id(text='originalId'))
    new_entry = self.batch_feed.AddBatchEntry(entry=to_add, 
                                              batch_id_string='foo')
    self.assertEqual(new_entry.batch_id.text, 'foo')
    self.assertEqual(new_entry.id.text, 'originalId')

    to_add = gdata.BatchEntry(atom_id=atom.Id(text='originalId'), 
                              batch_id=gdata.BatchId(text='bar'))
    new_entry = self.batch_feed.AddBatchEntry(entry=to_add, 
                                              id_url_string='newId',
                                              batch_id_string='foo')
    self.assertEqual(new_entry.batch_id.text, 'foo')
    self.assertEqual(new_entry.id.text, 'originalId')

    to_add = gdata.BatchEntry(atom_id=atom.Id(text='originalId'), 
                              batch_id=gdata.BatchId(text='bar'))
    new_entry = self.batch_feed.AddBatchEntry(entry=to_add, 
                                              id_url_string='newId')
    self.assertEqual(new_entry.batch_id.text, 'bar')
    self.assertEqual(new_entry.id.text, 'originalId')

    to_add = gdata.BatchEntry(atom_id=atom.Id(text='originalId'), 
                              batch_id=gdata.BatchId(text='bar'),
                              batch_operation=gdata.BatchOperation(
                                  op_type=gdata.BATCH_INSERT))
    self.assertEqual(to_add.batch_operation.type, gdata.BATCH_INSERT)
    new_entry = self.batch_feed.AddBatchEntry(entry=to_add, 
        id_url_string='newId', batch_id_string='foo', 
        operation_string=gdata.BATCH_UPDATE)
    self.assertEqual(new_entry.batch_operation.type, gdata.BATCH_UPDATE)


  def testAddInsert(self):
    
    first_entry = gdata.BatchEntry(
        atom_id=atom.Id(text='http://example.com/1'), text='This is a test1')
    self.batch_feed.AddInsert(first_entry)
    self.assertEqual(self.batch_feed.entry[0].batch_operation.type, 
                      gdata.BATCH_INSERT)
    self.assertEqual(self.batch_feed.entry[0].batch_id.text, '0')

    second_entry = gdata.BatchEntry(
        atom_id=atom.Id(text='http://example.com/2'), text='This is a test2')
    self.batch_feed.AddInsert(second_entry, batch_id_string='foo')
    self.assertEqual(self.batch_feed.entry[1].batch_operation.type, 
                      gdata.BATCH_INSERT)
    self.assertEqual(self.batch_feed.entry[1].batch_id.text, 'foo')

    
    third_entry = gdata.BatchEntry(
        atom_id=atom.Id(text='http://example.com/3'), text='This is a test3')
    third_entry.batch_operation = gdata.BatchOperation(
        op_type=gdata.BATCH_DELETE)
    # Add an entry with a delete operation already assigned.
    self.batch_feed.AddInsert(third_entry)
    # The batch entry should not have the original operation, it should 
    # have been changed to an insert.
    self.assertEqual(self.batch_feed.entry[2].batch_operation.type, 
                      gdata.BATCH_INSERT)
    self.assertEqual(self.batch_feed.entry[2].batch_id.text, '2')

  def testAddDelete(self):
    # Try deleting an entry
    delete_entry = gdata.BatchEntry(
        atom_id=atom.Id(text='http://example.com/1'), text='This is a test')
    self.batch_feed.AddDelete(entry=delete_entry)
    self.assertEqual(self.batch_feed.entry[0].batch_operation.type, 
                      gdata.BATCH_DELETE)
    self.assertEqual(self.batch_feed.entry[0].id.text, 
                      'http://example.com/1')
    self.assertEqual(self.batch_feed.entry[0].text, 'This is a test') 

    # Try deleting a URL
    self.batch_feed.AddDelete(url_string='http://example.com/2')
    self.assertEqual(self.batch_feed.entry[0].batch_operation.type, 
                      gdata.BATCH_DELETE)
    self.assertEqual(self.batch_feed.entry[1].id.text, 
                      'http://example.com/2')
    self.assertTrue(self.batch_feed.entry[1].text is None) 

  def testAddQuery(self):
    # Try querying with an existing batch entry
    delete_entry = gdata.BatchEntry(
        atom_id=atom.Id(text='http://example.com/1'))
    self.batch_feed.AddQuery(entry=delete_entry)
    self.assertEqual(self.batch_feed.entry[0].batch_operation.type,
                      gdata.BATCH_QUERY)
    self.assertEqual(self.batch_feed.entry[0].id.text,
                      'http://example.com/1')

    # Try querying a URL
    self.batch_feed.AddQuery(url_string='http://example.com/2')
    self.assertEqual(self.batch_feed.entry[0].batch_operation.type,
                      gdata.BATCH_QUERY)
    self.assertEqual(self.batch_feed.entry[1].id.text,
                      'http://example.com/2')

  def testAddUpdate(self):
    # Try updating an entry
    delete_entry = gdata.BatchEntry(
        atom_id=atom.Id(text='http://example.com/1'), text='This is a test')
    self.batch_feed.AddUpdate(entry=delete_entry)
    self.assertEqual(self.batch_feed.entry[0].batch_operation.type,
                      gdata.BATCH_UPDATE)
    self.assertEqual(self.batch_feed.entry[0].id.text,
                      'http://example.com/1')
    self.assertEqual(self.batch_feed.entry[0].text, 'This is a test')


class ExtendedPropertyTest(unittest.TestCase):
  
  def testXmlBlobRoundTrip(self):
    ep = gdata.ExtendedProperty(name='blobby')
    ep.SetXmlBlob('<some_xml attr="test"/>')
    extension = ep.GetXmlBlobExtensionElement()
    self.assertEqual(extension.tag, 'some_xml')
    self.assertTrue(extension.namespace is None)
    self.assertEqual(extension.attributes['attr'], 'test')

    ep2 = gdata.ExtendedPropertyFromString(ep.ToString())

    extension = ep2.GetXmlBlobExtensionElement()
    self.assertEqual(extension.tag, 'some_xml')
    self.assertTrue(extension.namespace is None)
    self.assertEqual(extension.attributes['attr'], 'test')

  def testGettersShouldReturnNoneWithNoBlob(self):
    ep = gdata.ExtendedProperty(name='no blob')
    self.assertTrue(ep.GetXmlBlobExtensionElement() is None)
    self.assertTrue(ep.GetXmlBlobString() is None)

  def testGettersReturnCorrectTypes(self):
    ep = gdata.ExtendedProperty(name='has blob')
    ep.SetXmlBlob('<some_xml attr="test"/>')
    self.assertTrue(isinstance(ep.GetXmlBlobExtensionElement(), 
        atom.ExtensionElement))
    self.assertTrue(isinstance(ep.GetXmlBlobString(), str))


class FeedLinkTest(unittest.TestCase):
  
  def testCorrectFromStringType(self):
    link = gdata.FeedLinkFromString(
        '<feedLink xmlns="http://schemas.google.com/g/2005" countHint="5"/>')
    self.assertTrue(isinstance(link, gdata.FeedLink))
    self.assertEqual(link.count_hint, '5')


def suite():
  return conf.build_suite([StartIndexTest, StartIndexTest, GDataEntryTest,
      LinkFinderTest, GDataFeedTest, BatchEntryTest, BatchFeedTest,
      ExtendedPropertyTest, FeedLinkTest])


if __name__ == '__main__':
  unittest.main()
