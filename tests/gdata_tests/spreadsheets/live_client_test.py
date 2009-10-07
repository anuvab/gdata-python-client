#!/usr/bin/env python
#
# Copyright (C) 2009 Google Inc.
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


# This module is used for version 2 of the Google Data APIs.
# These tests attempt to connect to Google servers.


__author__ = 'j.s@google.com (Jeff Scudder)'


import unittest
import gdata.spreadsheets.client
import gdata.gauth
import gdata.client
import atom.http_core
import atom.mock_http_core
import atom.core
import gdata.data
import gdata.test_config as conf


conf.options.register_option(conf.SPREADSHEET_ID_OPTION)


class SpreadsheetsClientTest(unittest.TestCase):

  def setUp(self):
    self.client = None
    if conf.options.get_value('runlive') == 'true':
      self.client = gdata.spreadsheets.client.SpreadsheetsClient()
      conf.configure_client(self.client, 'SpreadsheetsClientTest', 'wise')

  def tearDown(self):
    conf.close_client(self.client)

  def test_create_update_delete_worksheet(self):
    if not conf.options.get_value('runlive') == 'true':
      return
    # Either load the recording or prepare to make a live request.
    conf.configure_cache(self.client, 'test_create_update_delete_worksheet')

    spreadsheet_id = conf.options.get_value('spreadsheetid')
    original_worksheets = self.client.get_worksheets(spreadsheet_id)
    self.assertTrue(isinstance(original_worksheets,
                               gdata.spreadsheets.data.WorksheetsFeed))
    worksheet_count = int(original_worksheets.total_results.text)

    # Add a new worksheet to the spreadsheet.
    created = self.client.add_worksheet(
        spreadsheet_id, 'a test worksheet', 4, 8)
    self.assertTrue(isinstance(created,
                               gdata.spreadsheets.data.WorksheetEntry))
    self.assertEqual(created.title.text, 'a test worksheet')
    self.assertEqual(created.row_count.text, '4')
    self.assertEqual(created.col_count.text, '8')

    # There should now be one more worksheet in this spreadsheet.
    updated_worksheets = self.client.get_worksheets(spreadsheet_id)
    new_worksheet_count = int(updated_worksheets.total_results.text)
    self.assertEqual(worksheet_count + 1, new_worksheet_count)

    # Delete our test worksheet.
    self.client.delete(created)
    # We should be back to the original number of worksheets.
    updated_worksheets = self.client.get_worksheets(spreadsheet_id)
    new_worksheet_count = int(updated_worksheets.total_results.text)
    self.assertEqual(worksheet_count, new_worksheet_count)


def suite():
  return conf.build_suite([SpreadsheetsClientTest])


if __name__ == '__main__':
  unittest.TextTestRunner().run(suite())