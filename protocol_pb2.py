# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protocol.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='protocol.proto',
  package='',
  serialized_pb='\n\x0eprotocol.proto\"\xcf\x01\n\x04Post\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07subject\x18\x03 \x01(\t\x12\x0c\n\x04text\x18\x04 \x01(\t\x12\x0c\n\x04time\x18\x05 \x01(\x03\x12\x19\n\x05\x66iles\x18\x06 \x03(\x0b\x32\n.Post.File\x12\r\n\x05refer\x18\x07 \x01(\t\x12\x0c\n\x04tags\x18\x08 \x03(\t\x12\x11\n\tlanguages\x18\t \x03(\t\x1a\x35\n\x04\x46ile\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06source\x18\x02 \x01(\x0c\x12\x0f\n\x07md5hash\x18\x03 \x01(\t\"\xc1\x03\n\x04\x44\x61ta\x12\x16\n\x07sending\x18\x02 \x03(\x0b\x32\x05.Post\x12\x12\n\nrequesting\x18\x03 \x03(\t\x12!\n\x05known\x18\x04 \x03(\x0b\x32\x12.Data.ReceivedPost\x12\x1c\n\x04meta\x18\x05 \x01(\x0b\x32\x0e.Data.MetaData\x1a)\n\x04Host\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x02(\t\x12\x10\n\x08isPublic\x18\x02 \x01(\t\x1a\x86\x01\n\x0cReceivedPost\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0c\n\x04size\x18\x02 \x01(\x03\x12\x13\n\x0b\x66ile_hashes\x18\x03 \x03(\t\x12\x12\n\nfile_names\x18\x04 \x03(\t\x12\x12\n\nfile_sizes\x18\x05 \x03(\t\x12\x0c\n\x04tags\x18\x06 \x03(\t\x12\x11\n\tlanguages\x18\x07 \x03(\t\x1a\x97\x01\n\x08MetaData\x12\x11\n\tis_public\x18\x01 \x01(\x08\x12\x19\n\x11max_posts_at_once\x18\x02 \x01(\x03\x12\x14\n\x0clistening_on\x18\x03 \x01(\t\x12\x16\n\x0e\x61\x63\x63\x65pts_images\x18\x04 \x01(\x08\x12\x15\n\rmax_post_size\x18\x05 \x01(\x03\x12\x18\n\x10max_request_size\x18\x06 \x01(\x03')




_POST_FILE = _descriptor.Descriptor(
  name='File',
  full_name='Post.File',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Post.File.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source', full_name='Post.File.source', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='md5hash', full_name='Post.File.md5hash', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=173,
  serialized_end=226,
)

_POST = _descriptor.Descriptor(
  name='Post',
  full_name='Post',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Post.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='Post.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='subject', full_name='Post.subject', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='text', full_name='Post.text', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='time', full_name='Post.time', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='files', full_name='Post.files', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='refer', full_name='Post.refer', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tags', full_name='Post.tags', index=7,
      number=8, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='languages', full_name='Post.languages', index=8,
      number=9, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_POST_FILE, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=19,
  serialized_end=226,
)


_DATA_HOST = _descriptor.Descriptor(
  name='Host',
  full_name='Data.Host',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='Data.Host.address', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isPublic', full_name='Data.Host.isPublic', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=346,
  serialized_end=387,
)

_DATA_RECEIVEDPOST = _descriptor.Descriptor(
  name='ReceivedPost',
  full_name='Data.ReceivedPost',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Data.ReceivedPost.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='size', full_name='Data.ReceivedPost.size', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='file_hashes', full_name='Data.ReceivedPost.file_hashes', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='file_names', full_name='Data.ReceivedPost.file_names', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='file_sizes', full_name='Data.ReceivedPost.file_sizes', index=4,
      number=5, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tags', full_name='Data.ReceivedPost.tags', index=5,
      number=6, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='languages', full_name='Data.ReceivedPost.languages', index=6,
      number=7, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=390,
  serialized_end=524,
)

_DATA_METADATA = _descriptor.Descriptor(
  name='MetaData',
  full_name='Data.MetaData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='is_public', full_name='Data.MetaData.is_public', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_posts_at_once', full_name='Data.MetaData.max_posts_at_once', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='listening_on', full_name='Data.MetaData.listening_on', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='accepts_images', full_name='Data.MetaData.accepts_images', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_post_size', full_name='Data.MetaData.max_post_size', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_request_size', full_name='Data.MetaData.max_request_size', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=527,
  serialized_end=678,
)

_DATA = _descriptor.Descriptor(
  name='Data',
  full_name='Data',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sending', full_name='Data.sending', index=0,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='requesting', full_name='Data.requesting', index=1,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='known', full_name='Data.known', index=2,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='meta', full_name='Data.meta', index=3,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_DATA_HOST, _DATA_RECEIVEDPOST, _DATA_METADATA, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=229,
  serialized_end=678,
)

_POST_FILE.containing_type = _POST;
_POST.fields_by_name['files'].message_type = _POST_FILE
_DATA_HOST.containing_type = _DATA;
_DATA_RECEIVEDPOST.containing_type = _DATA;
_DATA_METADATA.containing_type = _DATA;
_DATA.fields_by_name['sending'].message_type = _POST
_DATA.fields_by_name['known'].message_type = _DATA_RECEIVEDPOST
_DATA.fields_by_name['meta'].message_type = _DATA_METADATA
DESCRIPTOR.message_types_by_name['Post'] = _POST
DESCRIPTOR.message_types_by_name['Data'] = _DATA

class Post(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class File(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _POST_FILE

    # @@protoc_insertion_point(class_scope:Post.File)
  DESCRIPTOR = _POST

  # @@protoc_insertion_point(class_scope:Post)

class Data(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class Host(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _DATA_HOST

    # @@protoc_insertion_point(class_scope:Data.Host)

  class ReceivedPost(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _DATA_RECEIVEDPOST

    # @@protoc_insertion_point(class_scope:Data.ReceivedPost)

  class MetaData(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _DATA_METADATA

    # @@protoc_insertion_point(class_scope:Data.MetaData)
  DESCRIPTOR = _DATA

  # @@protoc_insertion_point(class_scope:Data)


# @@protoc_insertion_point(module_scope)
