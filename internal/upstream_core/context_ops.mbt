// Adapted from trkbt10/grib2_mbt@00c30ee9a31adca0a15157f1b93ac7269415b9d3.
// Apache-2.0. Modified for this module; see THIRD_PARTY.md and UPSTREAM-LOCK.json.

///|
fn parse_single_message(
  raw : Bytes,
) -> Result[@context.Grib2MessageContext, @context.Grib2ContextEditError] {
  match parse_grib2_file(raw) {
    Ok(context) =>
      if context.messages.length() != 1 {
        Err(
          @context.Grib2ContextEditError::InvalidRawMessage(
            "expected exactly one message in raw bytes, found " +
            context.messages.length().to_string(),
          ),
        )
      } else {
        Ok(context.messages[0])
      }
    Err(error) => Err(@context.Grib2ContextEditError::ParseError(error))
  }
}

///|
pub fn context_replace_message_raw(
  context : @context.Grib2FileContext,
  message_index : Int,
  raw : Bytes,
) -> Result[@context.Grib2FileContext, @context.Grib2ContextEditError] {
  if message_index < 0 || message_index >= context.messages.length() {
    return Err(
      @context.Grib2ContextEditError::InvalidMessageIndex(
        "message index out of range: " +
        message_index.to_string() +
        " (len=" +
        context.messages.length().to_string() +
        ")",
      ),
    )
  }
  let parsed = match parse_single_message(raw) {
    Ok(message) => message
    Err(error) => return Err(error)
  }
  let messages = [..context.messages]
  messages[message_index] = parsed
  Ok({ messages: @context.reindex_messages(messages), })
}

///|
pub fn context_insert_message_raw(
  context : @context.Grib2FileContext,
  message_index : Int,
  raw : Bytes,
) -> Result[@context.Grib2FileContext, @context.Grib2ContextEditError] {
  if message_index < 0 || message_index > context.messages.length() {
    return Err(
      @context.Grib2ContextEditError::InvalidMessageIndex(
        "message index out of range for insert: " +
        message_index.to_string() +
        " (len=" +
        context.messages.length().to_string() +
        ")",
      ),
    )
  }
  let parsed = match parse_single_message(raw) {
    Ok(message) => message
    Err(error) => return Err(error)
  }
  let messages : Array[@context.Grib2MessageContext] = []
  for i in 0..<context.messages.length() {
    if i == message_index {
      messages.push(parsed)
    }
    messages.push(context.messages[i])
  }
  if message_index == context.messages.length() {
    messages.push(parsed)
  }
  Ok({ messages: @context.reindex_messages(messages), })
}

///|
pub fn context_append_message_raw(
  context : @context.Grib2FileContext,
  raw : Bytes,
) -> Result[@context.Grib2FileContext, @context.Grib2ContextEditError] {
  context_insert_message_raw(context, context.messages.length(), raw)
}

///|
pub fn context_remove_message(
  context : @context.Grib2FileContext,
  message_index : Int,
) -> Result[@context.Grib2FileContext, @context.Grib2ContextEditError] {
  if message_index < 0 || message_index >= context.messages.length() {
    return Err(
      @context.Grib2ContextEditError::InvalidMessageIndex(
        "message index out of range: " +
        message_index.to_string() +
        " (len=" +
        context.messages.length().to_string() +
        ")",
      ),
    )
  }
  let messages : Array[@context.Grib2MessageContext] = []
  for i in 0..<context.messages.length() {
    if i != message_index {
      messages.push(context.messages[i])
    }
  }
  Ok({ messages: @context.reindex_messages(messages), })
}
