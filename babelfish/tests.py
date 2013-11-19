#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 the BabelFish authors. All rights reserved.
# Use of this source code is governed by the 3-clause BSD license
# that can be found in the LICENSE file.
#
from __future__ import unicode_literals
from unittest import TestCase, TestSuite, TestLoader, TextTestRunner
from babelfish import (LANGUAGES, Language, Country, Script, get_language_converter, LANGUAGE_CONVERTERS,
    LanguageReverseConverter, load_language_converters, clear_language_converters, register_language_converter,
    unregister_language_converter, LanguageConvertError, LanguageReverseError)
from pkg_resources import resource_stream  # @UnresolvedImport


class TestScript(TestCase):
    def test_wrong_script(self):
        with self.assertRaises(ValueError):
            Script('Azer')

    def test_eq(self):
        self.assertTrue(Script('Latn') == Script('Latn'))

    def test_ne(self):
        self.assertTrue(Script('Cyrl') != Script('Latn'))

    def test_hash(self):
        self.assertTrue(hash(Script('Hira')) == hash('Hira'))


class TestCountry(TestCase):
    def test_wrong_country(self):
        with self.assertRaises(ValueError):
            Country('ZZ')

    def test_eq(self):
        self.assertTrue(Country('US') == Country('US'))

    def test_ne(self):
        self.assertTrue(Country('GB') != Country('US'))
        self.assertNotEqual(Country('US'), None)

    def test_hash(self):
        self.assertTrue(hash(Country('US')) == hash('US'))

    def test_name(self):
        self.assertEqual(Country('US').name, 'UNITED STATES')
        self.assertEqual(Country('FR').name, 'FRANCE')


class TestLanguage(TestCase):
    def test_languages(self):
        self.assertTrue(len(LANGUAGES) == 7874)

    def test_wrong_language(self):
        with self.assertRaises(ValueError):
            Language('zzz')

    def test_unknown_language(self):
        self.assertEqual(Language('zzzz', unknown='und'), Language('und'))

    def test_converter_alpha2(self):
        self.assertTrue(Language('eng').alpha2 == 'en')
        self.assertTrue(Language.fromalpha2('en') == Language('eng'))
        self.assertTrue(Language.fromcode('en', 'alpha2') == Language('eng'))
        with self.assertRaises(LanguageReverseError):
            Language.fromalpha2('zz')
        with self.assertRaises(LanguageConvertError):
            Language('aaa').alpha2
        self.assertTrue(len(get_language_converter('alpha2').codes) == 184)

    def test_converter_alpha3b(self):
        self.assertTrue(Language('fra').alpha3b == 'fre')
        self.assertTrue(Language.fromalpha3b('fre') == Language('fra'))
        self.assertTrue(Language.fromcode('fre', 'alpha3b') == Language('fra'))
        with self.assertRaises(LanguageReverseError):
            Language.fromalpha3b('zzz')
        with self.assertRaises(LanguageConvertError):
            Language('aaa').alpha3b
        self.assertTrue(len(get_language_converter('alpha3b').codes) == 418)

    def test_converter_name(self):
        self.assertTrue(Language('eng').name == 'English')
        self.assertTrue(Language.fromname('English') == Language('eng'))
        self.assertTrue(Language.fromcode('English', 'name') == Language('eng'))
        with self.assertRaises(LanguageReverseError):
            Language.fromname('Zzzzzzzzz')
        self.assertTrue(len(get_language_converter('name').codes) == 7874)

    def test_converter_scope(self):
        self.assertEqual(get_language_converter('scope').codes, {'I', 'S', 'M'})
        self.assertEqual(Language('eng').scope, 'individual')
        self.assertEqual(Language('und').scope, 'special')

    def test_converter_language_type(self):
        self.assertEqual(get_language_converter('type').codes, {'A', 'C', 'E', 'H', 'L', 'S'})
        self.assertEqual(Language('eng').type, 'living')
        self.assertEqual(Language('und').type, 'special')

    def test_converter_opensubtitles(self):
        self.assertTrue(Language('fra').opensubtitles == Language('fra').alpha3b)
        self.assertTrue(Language('por', 'BR').opensubtitles == 'pob')
        self.assertTrue(Language.fromopensubtitles('fre') == Language('fra'))
        self.assertTrue(Language.fromopensubtitles('pob') == Language('por', 'BR'))
        self.assertTrue(Language.fromopensubtitles('pb') == Language('por', 'BR'))
        # Montenegrin is not recognized as an ISO language (yet?) but for now it is
        # unofficially accepted as Serbian from Montenegro
        self.assertTrue(Language.fromopensubtitles('mne') == Language('srp', 'ME'))
        self.assertTrue(Language.fromcode('pob', 'opensubtitles') == Language('por', 'BR'))
        with self.assertRaises(LanguageReverseError):
            Language.fromopensubtitles('zzz')
        with self.assertRaises(LanguageConvertError):
            Language('aaa').opensubtitles
        self.assertEqual(len(get_language_converter('opensubtitles').codes), 606)

        # test with all the languages from the opensubtitles api
        # downloaded from: http://www.opensubtitles.org/addons/export_languages.php
        f = resource_stream('babelfish', 'data/opensubtitles_languages.txt')
        f.readline()
        for l in f:
            idlang, alpha2, _, upload_enabled, web_enabled = l.decode('utf-8').strip().split('\t')
            if not int(upload_enabled) and not int(web_enabled):
                # do not test languages that are too esoteric / not widely available
                continue
            self.assertEqual(Language.fromopensubtitles(idlang).opensubtitles, idlang)
            if alpha2:
                self.assertEqual(Language.fromopensubtitles(idlang), Language.fromopensubtitles(alpha2))
        f.close()

    def test_fromietf_country_script(self):
        language = Language.fromietf('fra-FR-Latn')
        self.assertTrue(language.alpha3 == 'fra')
        self.assertTrue(language.country == Country('FR'))
        self.assertTrue(language.script == Script('Latn'))

    def test_fromietf_country_no_script(self):
        language = Language.fromietf('fra-FR')
        self.assertTrue(language.alpha3 == 'fra')
        self.assertTrue(language.country == Country('FR'))
        self.assertTrue(language.script is None)

    def test_fromietf_no_country_no_script(self):
        language = Language.fromietf('fra-FR')
        self.assertTrue(language.alpha3 == 'fra')
        self.assertTrue(language.country == Country('FR'))
        self.assertTrue(language.script is None)

    def test_fromietf_no_country_script(self):
        language = Language.fromietf('fra-Latn')
        self.assertTrue(language.alpha3 == 'fra')
        self.assertTrue(language.country is None)
        self.assertTrue(language.script == Script('Latn'))

    def test_fromietf_alpha2_language(self):
        language = Language.fromietf('fr-Latn')
        self.assertTrue(language.alpha3 == 'fra')
        self.assertTrue(language.country is None)
        self.assertTrue(language.script == Script('Latn'))

    def test_fromietf_wrong_language(self):
        with self.assertRaises(ValueError):
            Language.fromietf('xyz-FR')

    def test_fromietf_wrong_country(self):
        with self.assertRaises(ValueError):
            Language.fromietf('fra-YZ')

    def test_fromietf_wrong_script(self):
        with self.assertRaises(ValueError):
            Language.fromietf('fra-FR-Wxyz')

    def test_eq(self):
        self.assertTrue(Language('eng') == Language('eng'))

    def test_ne(self):
        self.assertTrue(Language('fra') != Language('eng'))
        self.assertNotEqual(Language('fra'), None)

    def test_nonzero(self):
        self.assertTrue(bool(Language('und')) is False)
        self.assertTrue(bool(Language('eng')) is True)

    def test_country(self):
        self.assertTrue(Language('por', 'BR').country == Country('BR'))
        self.assertTrue(Language('eng', Country('US')).country == Country('US'))

    def test_eq_with_country(self):
        self.assertTrue(Language('eng', 'US') == Language('eng', Country('US')))

    def test_ne_with_country(self):
        self.assertTrue(Language('eng', 'US') != Language('eng', Country('GB')))

    def test_script(self):
        self.assertTrue(Language('srp', script='Latn').script == Script('Latn'))
        self.assertTrue(Language('srp', script=Script('Cyrl')).script == Script('Cyrl'))

    def test_eq_with_script(self):
        self.assertTrue(Language('srp', script='Latn') == Language('srp', script=Script('Latn')))

    def test_ne_with_script(self):
        self.assertTrue(Language('srp', script='Latn') != Language('srp', script=Script('Cyrl')))

    def test_eq_with_country_and_script(self):
        self.assertTrue(Language('srp', 'SR', 'Latn') == Language('srp', Country('SR'), Script('Latn')))

    def test_ne_with_country_and_script(self):
        self.assertTrue(Language('srp', 'SR', 'Latn') != Language('srp', Country('SR'), Script('Cyrl')))

    def test_hash(self):
        self.assertTrue(hash(Language('fra')) == hash('fr'))
        self.assertTrue(hash(Language('ace')) == hash('ace'))
        self.assertTrue(hash(Language('por', 'BR')) == hash('pt-BR'))
        self.assertTrue(hash(Language('srp', script='Cyrl')) == hash('sr-Cyrl'))
        self.assertTrue(hash(Language('eng', 'US', 'Latn')) == hash('en-US-Latn'))

    def test_str(self):
        self.assertTrue(Language.fromietf(str(Language('eng', 'US', 'Latn'))) == Language('eng', 'US', 'Latn'))
        self.assertTrue(Language.fromietf(str(Language('fra', 'FR'))) == Language('fra', 'FR'))
        self.assertTrue(Language.fromietf(str(Language('bel'))) == Language('bel'))

    def test_register_converter(self):
        class TestConverter(LanguageReverseConverter):
            def __init__(self):
                self.to_test = {'fra': 'test1', 'eng': 'test2'}
                self.from_test = {'test1': 'fra', 'test2': 'eng'}

            def convert(self, alpha3, country=None, script=None):
                if alpha3 not in self.to_test:
                    raise LanguageConvertError(alpha3, country, script)
                return self.to_test[alpha3]

            def reverse(self, test):
                if test not in self.from_test:
                    raise LanguageReverseError(test)
                return (self.from_test[test], None)
        language = Language('fra')
        self.assertTrue(not hasattr(language, 'test'))
        register_language_converter('test', TestConverter)
        self.assertTrue(hasattr(language, 'test'))
        self.assertTrue('test' in LANGUAGE_CONVERTERS)
        self.assertTrue(Language('fra').test == 'test1')
        self.assertTrue(Language.fromtest('test2').alpha3 == 'eng')
        unregister_language_converter('test')
        self.assertTrue('test' not in LANGUAGE_CONVERTERS)
        self.assertTrue(not hasattr(Language, 'fromtest'))
        with self.assertRaises(AttributeError):
            Language('fra').test
        clear_language_converters()
        load_language_converters()


def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestScript))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestCountry))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestLanguage))
    return suite


if __name__ == '__main__':
    TextTestRunner().run(suite())
