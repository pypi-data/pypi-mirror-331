'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
    Copyright (C) 2025  Nicholas Johnson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from dependency_injector.wiring import inject, Provide
from ..services import TranslationService
from ..containers import Container


@inject
def populate_spelling_system_table(
    spelling_system: str,
    translation_service: TranslationService = Provide[Container.translation_service]
):
    """Populate spelling system table with spelling system"""
    translation_service.add_spelling_system(spelling_system)
