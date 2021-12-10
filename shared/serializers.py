import pytz
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import empty
from django.db.models.query import QuerySet


class CustomModelSerializer(serializers.ModelSerializer):
    translate_fields = []

    def __init__(self, instance=None, data=None, extra_data={}, **kwargs):
        self.hide_serializer_fields = kwargs.pop(
            'hide_serializer_fields', False)
        if self.hide_serializer_fields:
            self.remove_serializer_fields(**kwargs)

        json_data = {}
        if data:
            for key in data:
                value = data.get(key, None)
                json_data[key] = value
        json_data.update(extra_data)

        super().__init__(instance=instance, data=(json_data or empty), **kwargs)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in self.translate_fields:
            fields[field].read_only = True
        return fields

    def remove_serializer_fields(self, **kwargs):
        serializer_fields = []
        for field_name in self.fields:
            if isinstance(self.fields[field_name], serializers.BaseSerializer):
                serializer_fields.append(field_name)
        for field_name in serializer_fields:
            self.fields.pop(field_name, None)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        for field_name in self.translate_fields:
            translated_value = ret.get(field_name + '_hi')
            if translated_value:
                ret[field_name] = translated_value
        return ret


class DateSerializerField(serializers.DateField):
    def to_internal_value(self, value):
        value = value.strip()
        try:
            value = timezone.datetime.strptime(
                value, '%b %d %Y').strftime('%Y-%m-%d')
        except Exception as e:
            pass
        return super().to_internal_value(value)

    def to_representation(self, key):
        return key.strftime("%d %B %Y")


class DateTimeSerializerField(serializers.DateTimeField):
    def to_representation(self, key):
        # tz = timezone.get_default_timezone()
        tz = pytz.timezone('Asia/Calcutta')
        key = timezone.localtime(key, timezone=tz)
        return key.strftime("%d %B %Y %I:%M %p")


class ChoicesField(serializers.Field):
    def __init__(self, choices, allow_custom=False, **kwargs):
        if not isinstance(choices, (tuple, list)):
            raise TypeError("choices must of type list or tuple")
        # value_to_key = {}
        for choice in choices:
            if len(choice) != 2:
                raise TypeError(
                    "choices must of type list or tuple with 2 columns")
            # value_to_key[choice[1]] = choice[0]

        # self._value_to_key = value_to_key
        self._key_to_value = dict(choices)
        self._allow_custom = allow_custom
        try:
            choice_type = type(choices[0][0])
            self._choice_type = choice_type if callable(choice_type) else None
        except Exception as e:
            self._choice_type = None
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, key):
        # database to json
        try:
            ans = {
                'key': key,
                'value': self._key_to_value[key],
            }
            return ans
        except:
            if self._allow_custom:
                ans = {
                    'key': key,
                    'value': key,
                }
                return ans

    def to_internal_value(self, value):
        try:
            if self._choice_type is not None:
                value = self._choice_type(value)
            if value in self._key_to_value:
                return value
        except Exception as e:
            pass
        raise serializers.ValidationError("Invalid field value {value}")


class MultipleSelectChoicesField(serializers.Field):
    # choices must have a two way mapping with unique keys, values
    def __init__(self, choices, allow_custom=False, flat=False, delimeter=",", **kwargs):
        if not isinstance(delimeter, str):
            raise TypeError("delimeter must of type str")
        if not isinstance(choices, (tuple, list)):
            raise TypeError("choices must of type list or tuple")
        # value_to_key = {}
        key_to_value = {}
        for choice in choices:
            if len(choice) != 2:
                raise TypeError(
                    "choices must of type list or tuple with 2 columns")
            if delimeter in choice[1]:
                raise ValueError(
                    "Invalid delimeter: delimeter must not be present in value {choice[1]}")
            if choice[0] in key_to_value:
                raise KeyError("key {choice[0]} has more than one values")
            # if choice[1] in value_to_key:
            #     raise KeyError("value {} has more than one keys".format(choice[1]))
            key_to_value[choice[0]] = choice[1]
            # value_to_key[choice[1]] = choice[0]

        # self._value_to_key = value_to_key
        self._key_to_value = key_to_value
        self._allow_custom = allow_custom
        self._delimeter = delimeter
        try:
            choice_type = type(choices[0][0])
            self._choice_type = choice_type if callable(choice_type) else None
        except Exception as e:
            self._choice_type = None
        self._flat = flat
        super(MultipleSelectChoicesField, self).__init__(**kwargs)

    def to_representation(self, keys):
        # database to json
        values = []
        for key in keys.split(self._delimeter):
            if not key:
                continue
            curr = None
            try:
                if self._choice_type is not None:
                    key = self._choice_type(key)
                if self._flat:
                    curr = self._key_to_value[key]
                else:
                    curr = {
                        'key': key,
                        'value': self._key_to_value[key],
                    }
            except Exception as e:
                if self._allow_custom:
                    if self._flat:
                        curr = key
                    else:
                        curr = {
                            'key': key,
                            'value': key,
                        }
            if curr:
                values.append(curr)
        if self._flat:
            return ', '.join(values)
        return values

    def to_internal_value(self, values):
        # json to database
        keys = []
        values_list = []
        if isinstance(values, (list, tuple)):
            values_list = values
        elif isinstance(values, str):
            values_list = values.split(self._delimeter)
        elif isinstance(values, int):
            values_list = [values]
        for value in values_list:
            if not value:
                continue
            curr = None
            try:
                if self._choice_type is not None:
                    value = self._choice_type(value)
                if value in self._key_to_value:
                    curr = str(value)
            except Exception as e:
                if self._allow_custom:
                    curr = str(value)
                else:
                    raise serializers.ValidationError(
                        f"Invalid field value {value}")
            if curr and curr not in keys:
                keys.append(curr)
        return self._delimeter.join(keys)
