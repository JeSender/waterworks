package com.waterworks.meterreading.utils;

import com.waterworks.meterreading.models.WaterRates;
import com.waterworks.meterreading.models.RateTier;
import java.util.ArrayList;
import java.util.List;

/**
 * Billing Calculator for Waterworks Tiered Rate System
 *
 * This calculator implements the exact same logic used in the backend
 * to ensure 100% accuracy in bill estimation.
 */
public class BillingCalculator {

    /**
     * Calculate water bill using tiered rate structure
     *
     * @param consumption Water consumption in cubic meters (m³)
     * @param usageType "Residential" or "Commercial"
     * @param rates Current water rates fetched from API
     * @return Calculated bill amount in pesos
     */
    public static double calculateBill(int consumption, String usageType, WaterRates rates) {
        RateTier tier = usageType.equals("Residential") ? rates.residential : rates.commercial;

        if (consumption <= 0) return 0.0;

        double bill = 0.0;
        int remaining = consumption;

        // Tier 1: 1-5 m³ (Minimum Charge - flat rate)
        if (remaining > 0) {
            bill += tier.minimum_charge;
            remaining -= 5;
        }

        // Tier 2: 6-10 m³ (5 m³ at tier 2 rate)
        if (remaining > 0) {
            int tier2Amount = Math.min(remaining, 5);
            bill += tier2Amount * tier.tier2_rate;
            remaining -= tier2Amount;
        }

        // Tier 3: 11-20 m³ (10 m³ at tier 3 rate)
        if (remaining > 0) {
            int tier3Amount = Math.min(remaining, 10);
            bill += tier3Amount * tier.tier3_rate;
            remaining -= tier3Amount;
        }

        // Tier 4: 21-50 m³ (30 m³ at tier 4 rate)
        if (remaining > 0) {
            int tier4Amount = Math.min(remaining, 30);
            bill += tier4Amount * tier.tier4_rate;
            remaining -= tier4Amount;
        }

        // Tier 5: 51+ m³ (unlimited at tier 5 rate)
        if (remaining > 0) {
            bill += remaining * tier.tier5_rate;
        }

        return bill;
    }

    /**
     * Get detailed billing breakdown for display to user
     * Shows exactly how the bill is calculated tier by tier
     */
    public static BillingBreakdown getBillingBreakdown(int consumption, String usageType, WaterRates rates) {
        RateTier tier = usageType.equals("Residential") ? rates.residential : rates.commercial;
        List<TierDetail> tiers = new ArrayList<>();
        int remaining = consumption;
        double total = 0.0;

        // Tier 1: 1-5 m³
        if (remaining > 0) {
            int consumed = Math.min(remaining, 5);
            tiers.add(new TierDetail(
                "Tier 1 (1-5 m³)",
                consumed,
                tier.minimum_charge / 5.0,  // For display purposes
                tier.minimum_charge,
                true
            ));
            total += tier.minimum_charge;
            remaining -= 5;  // Always subtract 5, even if consumption is less
        }

        // Tier 2: 6-10 m³
        if (remaining > 0) {
            int consumed = Math.min(remaining, 5);
            double cost = consumed * tier.tier2_rate;
            tiers.add(new TierDetail(
                "Tier 2 (6-10 m³)",
                consumed,
                tier.tier2_rate,
                cost,
                false
            ));
            total += cost;
            remaining -= consumed;
        }

        // Tier 3: 11-20 m³
        if (remaining > 0) {
            int consumed = Math.min(remaining, 10);
            double cost = consumed * tier.tier3_rate;
            tiers.add(new TierDetail(
                "Tier 3 (11-20 m³)",
                consumed,
                tier.tier3_rate,
                cost,
                false
            ));
            total += cost;
            remaining -= consumed;
        }

        // Tier 4: 21-50 m³
        if (remaining > 0) {
            int consumed = Math.min(remaining, 30);
            double cost = consumed * tier.tier4_rate;
            tiers.add(new TierDetail(
                "Tier 4 (21-50 m³)",
                consumed,
                tier.tier4_rate,
                cost,
                false
            ));
            total += cost;
            remaining -= consumed;
        }

        // Tier 5: 51+ m³
        if (remaining > 0) {
            double cost = remaining * tier.tier5_rate;
            tiers.add(new TierDetail(
                "Tier 5 (51+ m³)",
                remaining,
                tier.tier5_rate,
                cost,
                false
            ));
            total += cost;
        }

        return new BillingBreakdown(tiers, total);
    }

    /**
     * Validate reading value
     */
    public static ReadingValidation validateReading(int newReading, int previousReading) {
        if (newReading < 0) {
            return new ReadingValidation(
                false,
                "Reading cannot be negative",
                false
            );
        }

        if (newReading < previousReading) {
            return new ReadingValidation(
                false,
                "New reading must be greater than or equal to previous reading (" + previousReading + " m³)",
                false
            );
        }

        if (newReading == previousReading) {
            return new ReadingValidation(
                true,
                "Zero consumption detected",
                true
            );
        }

        if (newReading - previousReading > 1000) {
            return new ReadingValidation(
                true,
                "High consumption detected (" + (newReading - previousReading) + " m³). Please verify.",
                true
            );
        }

        return new ReadingValidation(
            true,
            "Reading is valid",
            false
        );
    }

    // ============================================================================
    // Inner Classes
    // ============================================================================

    /**
     * Data class for billing breakdown display
     */
    public static class BillingBreakdown {
        public List<TierDetail> tiers;
        public double total;

        public BillingBreakdown(List<TierDetail> tiers, double total) {
            this.tiers = tiers;
            this.total = total;
        }

        public String getFormattedTotal() {
            return String.format("₱%.2f", total);
        }
    }

    /**
     * Individual tier detail for breakdown
     */
    public static class TierDetail {
        public String tierName;
        public int cubicMeters;
        public double ratePerCubic;
        public double subtotal;
        public boolean isMinimumCharge;

        public TierDetail(String tierName, int cubicMeters, double ratePerCubic,
                         double subtotal, boolean isMinimumCharge) {
            this.tierName = tierName;
            this.cubicMeters = cubicMeters;
            this.ratePerCubic = ratePerCubic;
            this.subtotal = subtotal;
            this.isMinimumCharge = isMinimumCharge;
        }

        public String getFormattedAmount() {
            if (isMinimumCharge) {
                return "Minimum charge";
            } else {
                return String.format("%d m³ × ₱%.2f", cubicMeters, ratePerCubic);
            }
        }

        public String getFormattedSubtotal() {
            return String.format("₱%.2f", subtotal);
        }
    }

    /**
     * Reading validation result
     */
    public static class ReadingValidation {
        public boolean isValid;
        public String message;
        public boolean isWarning;

        public ReadingValidation(boolean isValid, String message, boolean isWarning) {
            this.isValid = isValid;
            this.message = message;
            this.isWarning = isWarning;
        }
    }
}
