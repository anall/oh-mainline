# -*- coding: utf-8 -*-
from __future__ import absolute_import
# vim: set ai et ts=4 sw=4:

# This file is part of OpenHatch.
# Copyright (C) 2014 Elana Hashman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Imports {{{
import mysite.bugsets.views
import mysite.bugsets.models

from mysite.base.tests import TwillTests

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
# }}}


class BasicBugsetMainViewTests(TwillTests):
    def test_bugset_names_load(self):
        mysite.bugsets.models.BugSet.objects.create(name="best event")
        mysite.bugsets.models.BugSet.objects.create(name="bestest event")
        url = reverse(mysite.bugsets.views.main_index)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "best event")
        self.assertContains(response, "bestest event")

    def test_bugset_view_link(self):
        s = mysite.bugsets.models.BugSet.objects.create(name="best event")
        url = reverse(mysite.bugsets.views.main_index)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, s.get_absolute_url())


class BasicBugsetListViewTests(TwillTests):
    def test_bugset_listview_load(self):
        s = mysite.bugsets.models.BugSet.objects.create(name="test event")
        b = mysite.bugsets.models.AnnotatedBug.objects.create(
            url="http://openhatch.org/bugs/issue995",
        )
        s.bugs.add(b)
        url = reverse(mysite.bugsets.views.list_index, kwargs={
            'pk': 1,
            'slug': '',
        })
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "test event")
        self.assertContains(response, "http://openhatch.org/bugs/issue995")

    def test_bugset_listview_load_with_custom_name(self):
        s = mysite.bugsets.models.BugSet.objects.create(name="test event")
        b = mysite.bugsets.models.AnnotatedBug.objects.create(
            url="http://openhatch.org/bugs/issue995",
        )
        s.bugs.add(b)
        url = reverse(mysite.bugsets.views.list_index, kwargs={
            'pk': 1,
            'slug': 'best-event',  # this can be anything!
        })
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "test event")
        self.assertContains(response, "http://openhatch.org/bugs/issue995")

    def test_bugset_listview_load_empty(self):
        # Create set with no bugs
        mysite.bugsets.models.BugSet.objects.create(name="test event")
        url = reverse(mysite.bugsets.views.list_index, kwargs={
            'pk': 1,
            'slug': '',
        })
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "test event")
        self.assertContains(response, "No bugs!")

    def test_bugset_listview_load_no_project(self):
        # Create set with no bugs
        s = mysite.bugsets.models.BugSet.objects.create(name="test event")
        b = mysite.bugsets.models.AnnotatedBug.objects.create(
            url="http://openhatch.org/bugs/issue995",
        )
        s.bugs.add(b)

        url = reverse(mysite.bugsets.views.list_index, kwargs={
            'pk': 1,
            'slug': '',
        })
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "test event")
        self.assertContains(response, "http://openhatch.org/bugs/issue995")
        self.assertContains(response, "�")  # the no project character

    def test_bugset_listview_load_with_annotated_bug(self):
        # Create set and a bug for it
        s = mysite.bugsets.models.BugSet.objects.create(name="test event")
        b = mysite.bugsets.models.AnnotatedBug.objects.create(
            url="http://openhatch.org/bugs/issue995",
        )

        # Annotate the bug
        b.title = "Add bug set view screen"
        b.description = ("Use your Django and HTML/CSS skills to make a nice "
                         "UI for the bug sets")
        b.assigned_to = "Jesse"
        b.mentor = "Elana"
        b.time_estimate = "2 hours"
        b.status = "c"
        b.skill_list = "python, html"

        # Make a project
        p = mysite.search.models.Project.objects.create(
            name='openhatch',
            display_name='OpenHatch DisplayName',
            homepage='http://openhatch.org',
            language='Python',
        )
        p.save()
        b.project = p

        # Save and associate with bugset
        b.save()
        s.bugs.add(b)

        url = reverse(mysite.bugsets.views.list_index, kwargs={
            'pk': 1,
            'slug': '',
        })
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "test event")
        self.assertContains(response, "http://openhatch.org/bugs/issue995")
        self.assertContains(response, "OpenHatch DisplayName")
        self.assertContains(response, "Add bug set view screen")
        self.assertContains(response, ("Use your Django and HTML/CSS skills "
                                       "to make a nice UI for the bug sets"))
        self.assertContains(response, "Jesse")
        self.assertContains(response, "Elana")
        self.assertContains(response, "2 hours")
        self.assertContains(response, "claimed")
        self.assertContains(response, "python, html")


class SecurityBugsetListViewTests(TwillTests):
    def test_will_inplaceedit_allow_us_to_pwn_ourselves(self):
        # Asheesh: "total cost of pwnership: 1 test"
        # note: user paulproteus has poor password hygiene
        u = User.objects.create(username='paulproteus', password='password')
        u.save()

        self.client.post(
            '/inplaceeditform/save/',
            {
                "app_label": "auth",      # the django app
                "module_name": "user",    # the django table
                "field_name": "username", # the field name
                "obj_id": u.pk,           # the pk
                "value": '"LOLPWNED"'     # new value
            })
 
        self.assertEqual(User.objects.get(pk=u.pk).username, u'paulproteus')


class BasicBugsetCreateViewTests(TwillTests):
    def test_create_view_load(self):
        url = reverse(mysite.bugsets.views.create_index)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Create a Bug Set")
