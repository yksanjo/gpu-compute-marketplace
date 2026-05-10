-- Token System Database Schema

-- Users table (simplified)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Token accounts (one per user)
CREATE TABLE token_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    active_balance DECIMAL(15, 4) NOT NULL DEFAULT 0,
    reserved_balance DECIMAL(15, 4) NOT NULL DEFAULT 0,
    total_purchased DECIMAL(15, 4) NOT NULL DEFAULT 0,
    total_consumed DECIMAL(15, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Token transactions (all token movements)
CREATE TABLE token_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES token_accounts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'purchase', 'subscription', 'reservation', 'consumption', 'refund', 'expiration', 'promotion'
    amount DECIMAL(15, 4) NOT NULL,
    balance_before DECIMAL(15, 4) NOT NULL,
    balance_after DECIMAL(15, 4) NOT NULL,
    metadata JSONB, -- Additional context (job_id, gpu_type, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Token allocations (tokens with expiration)
CREATE TABLE token_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES token_accounts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'prepaid', 'subscription', 'spot', 'enterprise'
    amount DECIMAL(15, 4) NOT NULL,
    remaining DECIMAL(15, 4) NOT NULL,
    expires_at TIMESTAMP,
    tier VARCHAR(50), -- 'on-demand', 'reserved', 'spot', 'subscription'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Token reservations (tokens allocated to jobs)
CREATE TABLE token_reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES token_accounts(id) ON DELETE CASCADE,
    job_id UUID NOT NULL, -- References compute_jobs table
    amount DECIMAL(15, 4) NOT NULL,
    gpu_type VARCHAR(50) NOT NULL,
    estimated_hours DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'active', 'consumed', 'refunded', 'expired'
    expires_at TIMESTAMP, -- Reservation timeout
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Token purchases (payment records)
CREATE TABLE token_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES token_accounts(id) ON DELETE CASCADE,
    amount_cc DECIMAL(15, 4) NOT NULL, -- Tokens purchased
    amount_fiat DECIMAL(15, 2) NOT NULL, -- Fiat amount paid
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL,
    payment_provider VARCHAR(50), -- 'stripe', 'paypal', etc.
    payment_id VARCHAR(255), -- External payment ID
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_token_accounts_user_id ON token_accounts(user_id);
CREATE INDEX idx_token_transactions_user_id ON token_transactions(user_id);
CREATE INDEX idx_token_transactions_account_id ON token_transactions(account_id);
CREATE INDEX idx_token_transactions_created_at ON token_transactions(created_at);
CREATE INDEX idx_token_allocations_account_id ON token_allocations(account_id);
CREATE INDEX idx_token_allocations_expires_at ON token_allocations(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_token_reservations_account_id ON token_reservations(account_id);
CREATE INDEX idx_token_reservations_job_id ON token_reservations(job_id);
CREATE INDEX idx_token_reservations_status ON token_reservations(status);
CREATE INDEX idx_token_purchases_user_id ON token_purchases(user_id);
CREATE INDEX idx_token_purchases_status ON token_purchases(status);

-- Function to update token account balance
CREATE OR REPLACE FUNCTION update_token_balance(
    p_account_id UUID,
    p_amount DECIMAL,
    p_type VARCHAR -- 'active', 'reserved'
) RETURNS VOID AS $$
BEGIN
    IF p_type = 'active' THEN
        UPDATE token_accounts
        SET active_balance = active_balance + p_amount,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = p_account_id;
    ELSIF p_type = 'reserved' THEN
        UPDATE token_accounts
        SET reserved_balance = reserved_balance + p_amount,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = p_account_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to record token transaction
CREATE OR REPLACE FUNCTION record_token_transaction(
    p_user_id UUID,
    p_account_id UUID,
    p_type VARCHAR,
    p_amount DECIMAL,
    p_metadata JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_balance_before DECIMAL;
    v_balance_after DECIMAL;
    v_transaction_id UUID;
BEGIN
    -- Get current balance
    SELECT active_balance INTO v_balance_before
    FROM token_accounts
    WHERE id = p_account_id;
    
    -- Calculate new balance
    v_balance_after := v_balance_before + p_amount;
    
    -- Insert transaction record
    INSERT INTO token_transactions (
        user_id, account_id, type, amount,
        balance_before, balance_after, metadata
    ) VALUES (
        p_user_id, p_account_id, p_type, p_amount,
        v_balance_before, v_balance_after, p_metadata
    ) RETURNING id INTO v_transaction_id;
    
    RETURN v_transaction_id;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_token_accounts_updated_at
    BEFORE UPDATE ON token_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_token_allocations_updated_at
    BEFORE UPDATE ON token_allocations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_token_reservations_updated_at
    BEFORE UPDATE ON token_reservations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

