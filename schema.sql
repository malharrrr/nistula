CREATE TYPE channel_type AS ENUM ('whatsapp', 'booking_com', 'airbnb', 'instagram', 'direct');
CREATE TYPE message_status AS ENUM ('ai_drafted', 'agent_edited', 'auto_sent', 'agent_sent');
CREATE TYPE action_type AS ENUM ('auto_send', 'agent_review', 'escalate');
CREATE TYPE query_class AS ENUM (
    'pre_sales_availability', 
    'pre_sales_pricing', 
    'post_sales_checkin', 
    'special_request', 
    'complaint', 
    'general_enquiry'
);

CREATE TABLE guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    primary_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE guest_identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID NOT NULL REFERENCES guests(id) ON DELETE CASCADE,
    channel channel_type NOT NULL,
    external_user_id VARCHAR(255) NOT NULL, -- e.g., phone number, Airbnb ID
    UNIQUE(channel, external_user_id)
);

CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID NOT NULL REFERENCES guests(id),
    property_id VARCHAR(100) NOT NULL,
    booking_ref VARCHAR(100) UNIQUE NOT NULL,
    check_in_date DATE,
    check_out_date DATE
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID NOT NULL REFERENCES guests(id),
    reservation_id UUID REFERENCES reservations(id), -- nullable for pre-sales conversation
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(50) CHECK (sender_type IN ('guest', 'system', 'agent')),
    channel channel_type NOT NULL,
    content TEXT NOT NULL,
    
    query_type query_class,
    confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    system_action action_type,
    delivery_status message_status,
    
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_guest_identities_lookup ON guest_identities(channel, external_user_id);