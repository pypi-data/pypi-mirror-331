# Copyright 2016- Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import annotations
from typing import *
from .AppleAppStoreSubscriptionContent import AppleAppStoreSubscriptionContent
from .GooglePlaySubscriptionContent import GooglePlaySubscriptionContent
from .options.StoreSubscriptionContentModelOptions import StoreSubscriptionContentModelOptions


class StoreSubscriptionContentModel:
    name: str
    schedule_namespace_id: str
    trigger_name: str
    reallocate_span_days: int
    metadata: Optional[str] = None
    apple_app_store: Optional[AppleAppStoreSubscriptionContent] = None
    google_play: Optional[GooglePlaySubscriptionContent] = None

    def __init__(
        self,
        name: str,
        schedule_namespace_id: str,
        trigger_name: str,
        reallocate_span_days: int,
        options: Optional[StoreSubscriptionContentModelOptions] = StoreSubscriptionContentModelOptions(),
    ):
        self.name = name
        self.schedule_namespace_id = schedule_namespace_id
        self.trigger_name = trigger_name
        self.reallocate_span_days = reallocate_span_days
        self.metadata = options.metadata if options.metadata else None
        self.apple_app_store = options.apple_app_store if options.apple_app_store else None
        self.google_play = options.google_play if options.google_play else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.schedule_namespace_id is not None:
            properties["scheduleNamespaceId"] = self.schedule_namespace_id
        if self.trigger_name is not None:
            properties["triggerName"] = self.trigger_name
        if self.reallocate_span_days is not None:
            properties["reallocateSpanDays"] = self.reallocate_span_days
        if self.apple_app_store is not None:
            properties["appleAppStore"] = self.apple_app_store.properties(
            )
        if self.google_play is not None:
            properties["googlePlay"] = self.google_play.properties(
            )

        return properties
