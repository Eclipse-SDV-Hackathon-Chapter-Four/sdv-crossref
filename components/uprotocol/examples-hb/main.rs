use std::sync::Arc;
use up_rust::{LocalUriProvider, StaticUriProvider, UListener, UMessage, UMessageBuilder, UPayloadFormat, UTransport, UUri};
use up_transport_zenoh::UPTransportZenoh;

struct Print;
#[async_trait::async_trait]
impl UListener for Print {
    async fn on_receive(&self, msg: UMessage) {
        let src = msg.attributes.as_ref().and_then(|a| a.source.as_ref()).map(|u| u.to_uri(false));
        let body = msg.payload.as_ref().map(|p| String::from_utf8_lossy(p).to_string());
        println!("got {:?} from {:?}", body, src);
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let role = std::env::args().nth(1).unwrap_or_default(); // "pub" or "sub"
    let name = if role == "pub" { "guardian" } else { "monitor" };
    let uri = StaticUriProvider::new(name, 0x1001, 1);
    let transport = Arc::new(UPTransportZenoh::builder(uri.get_authority())?.with_config(up_transport_zenoh::zenoh_config::Config::default()).build().await?);
    if role == "pub" {
        let topic = uri.get_resource_uri(0x8001); // heartbeat topic
        for i in 0.. {
            let m = UMessageBuilder::publish(topic.clone())
                .build_with_payload(format!("hb {i}"), UPayloadFormat::UPAYLOAD_FORMAT_TEXT)?;
            transport.send(m).await?;
            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        }
    } else {
        // any authority, entity 0x1001 (any instance), version 1, resource 0x8001
        let filter = UUri::try_from_parts("*", 0xFFFF_1001, 1, 0x8001)?;
        transport.register_listener(&filter, None, Arc::new(Print)).await?;
        tokio::time::sleep(std::time::Duration::from_secs(3600)).await;
    }
    Ok(())
}
